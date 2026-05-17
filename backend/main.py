import os
import uuid
import json
import asyncio
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from models.schemas import (
    AnalysisStartResponse, AnalysisResult, AgentEvent,
    AgentStatus, ErrorResponse
)
from services.document_parser import DocumentParser
from services.storage_client import StorageClient
from agents.crew_orchestrator import CrewOrchestrator

load_dotenv()

# ─────────────────────────────────────────
#  App Init
# ─────────────────────────────────────────
app = FastAPI(
    title="LexGuard X API",
    description="AI Rights & Contract Intelligence System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
#  In-Memory State Store
# ─────────────────────────────────────────
analysis_store: Dict[str, dict] = {}
ws_connections: Dict[str, WebSocket] = {}

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────
#  Allowed file types
# ─────────────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".tiff"}
MAX_FILE_SIZE_MB = 20


# ─────────────────────────────────────────
#  WebSocket Manager
# ─────────────────────────────────────────
async def broadcast_event(analysis_id: str, event: dict):
    """Send event to connected WebSocket client."""
    ws = ws_connections.get(analysis_id)
    if ws:
        try:
            await ws.send_json(event)
        except Exception as e:
            print(f"[WS] Broadcast error: {e}")


# ─────────────────────────────────────────
#  Background Analysis Runner
# ─────────────────────────────────────────
def run_analysis_in_thread(analysis_id: str, file_bytes: bytes, filename: str):
    """Runs the full agent pipeline in a background thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _run():
        try:
            # 1. Parse document
            parser = DocumentParser()
            storage = StorageClient()

            # Upload to GCS
            gcs_url = storage.upload_contract(file_bytes, filename, analysis_id)

            # Extract text
            await broadcast_event(analysis_id, {
                "agent_name": "Document Parser",
                "status": "running",
                "message": "Extracting text from document...",
                "progress": 1,
                "findings_count": 0
            })

            full_text = parser.parse(file_bytes, filename)

            if len(full_text.strip()) < 100:
                raise ValueError("Could not extract meaningful text from document.")

            await broadcast_event(analysis_id, {
                "agent_name": "Document Parser",
                "status": "done",
                "message": f"Extracted {len(full_text):,} characters",
                "progress": 5,
                "findings_count": 0
            })

            # 2. Run orchestrator with WebSocket progress callback
            def progress_cb(agent_name, status, message, progress, findings_count=0):
                event = {
                    "agent_name": agent_name,
                    "status": status.value if hasattr(status, 'value') else status,
                    "message": message,
                    "progress": progress,
                    "findings_count": findings_count
                }
                asyncio.run_coroutine_threadsafe(
                    broadcast_event(analysis_id, event), loop
                )

            orchestrator = CrewOrchestrator()
            result = orchestrator.run(analysis_id, full_text, filename, progress_cb)

            # 3. Store result
            result_dict = result.model_dump()
            analysis_store[analysis_id] = {
                "status": "complete",
                "result": result_dict,
                "gcs_url": gcs_url
            }

            # Upload report to GCS
            storage.upload_report(json.dumps(result_dict), analysis_id)

            # Send completion event
            await broadcast_event(analysis_id, {
                "agent_name": "System",
                "status": "complete",
                "message": "Analysis complete!",
                "progress": 100,
                "findings_count": len(result.findings),
                "analysis_id": analysis_id
            })

        except Exception as e:
            print(f"[Analysis Error] {analysis_id}: {e}")
            analysis_store[analysis_id] = {
                "status": "error",
                "error": str(e)
            }
            await broadcast_event(analysis_id, {
                "agent_name": "System",
                "status": "error",
                "message": f"Analysis failed: {str(e)}",
                "progress": 0,
                "findings_count": 0
            })

    loop.run_until_complete(_run())
    loop.close()


# ─────────────────────────────────────────
#  API Routes
# ─────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "LexGuard X API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/api/analyze", response_model=AnalysisStartResponse)
async def analyze_contract(file: UploadFile = File(...)):
    """
    Upload a contract file and start AI analysis.
    Returns an analysis_id for tracking via WebSocket.
    """
    # Validate file type
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file
    file_bytes = await file.read()

    # Validate file size
    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
        )

    # Generate analysis ID
    analysis_id = str(uuid.uuid4())

    # Store initial state
    analysis_store[analysis_id] = {
        "status": "processing",
        "filename": file.filename
    }

    # Start background analysis thread
    thread = threading.Thread(
        target=run_analysis_in_thread,
        args=(analysis_id, file_bytes, file.filename),
        daemon=True
    )
    thread.start()

    return AnalysisStartResponse(
        analysis_id=analysis_id,
        message="Analysis started. Connect to WebSocket for live updates.",
        status="processing"
    )


@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get the full analysis result for a completed analysis."""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")

    stored = analysis_store[analysis_id]
    if stored["status"] == "processing":
        return {"status": "processing", "analysis_id": analysis_id}
    elif stored["status"] == "error":
        raise HTTPException(status_code=500, detail=stored.get("error", "Analysis failed"))

    return stored["result"]


@app.get("/api/analysis/{analysis_id}/status")
async def get_analysis_status(analysis_id: str):
    """Get just the status of an analysis."""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    stored = analysis_store[analysis_id]
    return {
        "analysis_id": analysis_id,
        "status": stored.get("status", "unknown"),
        "filename": stored.get("filename", "")
    }


# ─────────────────────────────────────────
#  WebSocket Endpoint
# ─────────────────────────────────────────
@app.websocket("/ws/analysis/{analysis_id}")
async def websocket_analysis(websocket: WebSocket, analysis_id: str):
    """
    WebSocket endpoint for real-time agent progress updates.
    Frontend connects here to receive live agent activity feed.
    """
    await websocket.accept()
    ws_connections[analysis_id] = websocket

    try:
        # Check if analysis already complete
        if analysis_id in analysis_store:
            stored = analysis_store[analysis_id]
            if stored["status"] == "complete":
                await websocket.send_json({
                    "agent_name": "System",
                    "status": "complete",
                    "message": "Analysis already complete",
                    "progress": 100,
                    "findings_count": len(stored.get("result", {}).get("findings", [])),
                    "analysis_id": analysis_id
                })

        # Keep connection alive
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                # Send keepalive ping
                await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WS] Connection error: {e}")
    finally:
        ws_connections.pop(analysis_id, None)


# ─────────────────────────────────────────
#  Run
# ─────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
