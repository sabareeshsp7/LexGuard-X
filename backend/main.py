"""
LexGuard X — FastAPI Application Entry Point

Route map:
  GET  /api/health                       — Service health check
  POST /api/analyze                      — Upload contract, start analysis
  GET  /api/analysis/{id}                — Get full analysis result
  GET  /api/analysis/{id}/status         — Lightweight status poll
  GET  /api/history                      — Recent analyses (Firestore)
  GET  /api/tts/{id}/verdict             — TTS audio for verdict (accessibility)
  GET  /api/tts/{id}/finding/{clause_id} — TTS audio for a finding
  WS   /ws/analysis/{id}                 — Real-time WebSocket agent feed
"""

import os
import uuid
import json
import asyncio
import logging
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv

from models.schemas import (
    AnalysisStartResponse, AnalysisResult, AgentEvent,
    AgentStatus, ErrorResponse
)
from services.document_parser import DocumentParser
from services.storage_client import StorageClient
from services.firestore_client import FirestoreClient
from services.logging_client import cloud_logger
from services.tts_client import TTSClient
from services.nlp_client import NLPClient
from agents.crew_orchestrator import CrewOrchestrator

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────
#  App Init
# ─────────────────────────────────────────
app = FastAPI(
    title="LexGuard X API",
    description=(
        "AI-powered contract intelligence. Upload any legal document and "
        "get risk analysis, privacy audit, negotiation advice, and more — "
        "powered by Google Vertex AI Gemini 3.1 Flash Lite."
    ),
    version="1.0.0",
    contact={
        "name": "LexGuard X",
        "url": "https://github.com/sabareeshsp7/LexGuard-X",
    },
    license_info={"name": "MIT"},
)

# ─────────────────────────────────────────
#  CORS — restrict to known origins in production
# ─────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# ─────────────────────────────────────────
#  Shared service instances (singletons)
# ─────────────────────────────────────────
_storage = StorageClient()
_firestore = FirestoreClient()
_tts = TTSClient()
_nlp = NLPClient()

# ─────────────────────────────────────────
#  In-Memory State Store
#  (Firestore is the durable backing store)
# ─────────────────────────────────────────
analysis_store: Dict[str, dict] = {}
ws_connections: Dict[str, WebSocket] = {}

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────
#  File validation constants
# ─────────────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".tiff"}
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


# ─────────────────────────────────────────
#  WebSocket helpers
# ─────────────────────────────────────────
async def broadcast_event(analysis_id: str, event: dict) -> None:
    """Send a structured event to the connected WebSocket client."""
    ws = ws_connections.get(analysis_id)
    if ws:
        try:
            await ws.send_json(event)
        except Exception as exc:
            logger.warning("[WS] Broadcast error for %s: %s", analysis_id, exc)


# ─────────────────────────────────────────
#  Background Analysis Runner
# ─────────────────────────────────────────
def run_analysis_in_thread(
    analysis_id: str, file_bytes: bytes, filename: str
) -> None:
    """
    Runs the full 8-agent pipeline in a background daemon thread.
    Each agent broadcasts progress events via WebSocket.
    Results are persisted to both the in-memory store and Firestore.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def _run() -> None:
        import time
        pipeline_start = time.time()

        try:
            # ── Upload contract to GCS ─────────────────────────
            gcs_url = _storage.upload_contract(file_bytes, filename, analysis_id)
            cloud_logger.log_upload(analysis_id, filename, len(file_bytes))

            # ── Document parsing ───────────────────────────────
            await broadcast_event(analysis_id, {
                "agent_name": "Document Parser",
                "status": "running",
                "message": "Extracting text from document...",
                "progress": 1,
                "findings_count": 0,
            })

            parser = DocumentParser()
            full_text = parser.parse(file_bytes, filename)

            if len(full_text.strip()) < 100:
                raise ValueError(
                    "Could not extract meaningful text. "
                    "Ensure the document is not empty or password-protected."
                )

            await broadcast_event(analysis_id, {
                "agent_name": "Document Parser",
                "status": "done",
                "message": f"Extracted {len(full_text):,} characters",
                "progress": 5,
                "findings_count": 0,
            })

            # ── NLP enrichment (non-blocking, best-effort) ─────
            entities = []
            sentiment = {"score": 0.0, "magnitude": 0.0}
            if _nlp.is_available():
                try:
                    entities = _nlp.extract_entities(full_text)
                    sentiment = _nlp.analyze_sentiment(full_text)
                    logger.info(
                        "[NLP] %d entities extracted, sentiment=%.2f",
                        len(entities), sentiment.get("score", 0),
                    )
                except Exception as nlp_exc:
                    logger.warning("[NLP] Enrichment failed (non-fatal): %s", nlp_exc)

            # ── Agent pipeline ─────────────────────────────────
            def progress_cb(agent_name, status, message, progress, findings_count=0):
                event = {
                    "agent_name": agent_name,
                    "status": status.value if hasattr(status, "value") else status,
                    "message": message,
                    "progress": progress,
                    "findings_count": findings_count,
                }
                asyncio.run_coroutine_threadsafe(
                    broadcast_event(analysis_id, event), loop
                )

            orchestrator = CrewOrchestrator()
            result = orchestrator.run(analysis_id, full_text, filename, progress_cb)

            # ── Attach NLP metadata ────────────────────────────
            result_dict = result.model_dump()
            result_dict["nlp_entities"] = entities[:20]   # top-20 for payload size
            result_dict["sentiment"] = sentiment

            # ── Persist results ────────────────────────────────
            analysis_store[analysis_id] = {
                "status": "complete",
                "result": result_dict,
                "gcs_url": gcs_url,
            }

            _storage.upload_report(json.dumps(result_dict), analysis_id)
            _firestore.save_analysis_result(result_dict, gcs_url)  # type: ignore

            duration = round(time.time() - pipeline_start, 1)
            cloud_logger.log_analysis_complete(
                analysis_id,
                result.risk_score.overall_score,
                len(result.findings),
                duration,
            )

            # ── Completion broadcast ───────────────────────────
            await broadcast_event(analysis_id, {
                "agent_name": "System",
                "status": "complete",
                "message": "Analysis complete!",
                "progress": 100,
                "findings_count": len(result.findings),
                "analysis_id": analysis_id,
            })

        except Exception as exc:
            error_msg = str(exc)
            logger.error("[Analysis] %s failed: %s", analysis_id, error_msg)
            analysis_store[analysis_id] = {"status": "error", "error": error_msg}
            _firestore.mark_analysis_error(analysis_id, error_msg)
            cloud_logger.log_analysis_error(analysis_id, error_msg)

            await broadcast_event(analysis_id, {
                "agent_name": "System",
                "status": "error",
                "message": f"Analysis failed: {error_msg}",
                "progress": 0,
                "findings_count": 0,
            })

    loop.run_until_complete(_run())
    loop.close()


# ─────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────

@app.get(
    "/api/health",
    summary="Health check",
    tags=["System"],
)
async def health_check():
    """Return service health, version, and Google service availability."""
    return {
        "status": "healthy",
        "service": "LexGuard X API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "google_services": {
            "cloud_storage": _storage.enabled,
            "firestore": _firestore.enabled,
            "text_to_speech": _tts.enabled,
            "natural_language": _nlp.enabled,
        },
    }


@app.post(
    "/api/analyze",
    response_model=AnalysisStartResponse,
    summary="Upload contract and start AI analysis",
    tags=["Analysis"],
)
async def analyze_contract(file: UploadFile = File(...)):
    """
    Upload a contract document and begin the 8-agent AI analysis pipeline.

    - **Accepted formats:** PDF, DOCX, DOC, PNG, JPG, JPEG, TIFF
    - **Max file size:** 20 MB
    - **Returns:** `analysis_id` — use with WebSocket for live updates.
    """
    # Validate file object
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{ext}'. "
                f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )

    # Read and validate size
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB} MB",
        )

    # Generate analysis ID and bootstrap state
    analysis_id = str(uuid.uuid4())
    analysis_store[analysis_id] = {
        "status": "processing",
        "filename": file.filename,
    }
    _firestore.create_analysis_record(analysis_id, file.filename)

    # Kick off background thread
    thread = threading.Thread(
        target=run_analysis_in_thread,
        args=(analysis_id, file_bytes, file.filename),
        daemon=True,
        name=f"analysis-{analysis_id[:8]}",
    )
    thread.start()

    cloud_logger.info(
        f"Analysis started for '{file.filename}'",
        analysis_id=analysis_id,
        event="analysis_started",
    )

    return AnalysisStartResponse(
        analysis_id=analysis_id,
        message="Analysis started. Connect to WebSocket for live updates.",
        status="processing",
    )


@app.get(
    "/api/analysis/{analysis_id}",
    summary="Get full analysis result",
    tags=["Analysis"],
)
async def get_analysis(analysis_id: str):
    """
    Retrieve the complete analysis result for a finished analysis.

    Returns `{"status": "processing"}` if still running,
    or raises 404 if the analysis_id is unknown.
    """
    if not analysis_id or len(analysis_id) < 8:
        raise HTTPException(status_code=400, detail="Invalid analysis_id format")

    stored = analysis_store.get(analysis_id)

    # Fall back to Firestore if not in memory (e.g. after server restart)
    if stored is None:
        firestore_record = _firestore.get_analysis(analysis_id)
        if firestore_record:
            if firestore_record.get("status") == "complete":
                return firestore_record.get("result", firestore_record)
            stored = firestore_record
        else:
            raise HTTPException(status_code=404, detail="Analysis not found")

    if stored["status"] == "processing":
        return {"status": "processing", "analysis_id": analysis_id}
    if stored["status"] == "error":
        raise HTTPException(
            status_code=500,
            detail=stored.get("error", "Analysis failed unexpectedly"),
        )

    return stored["result"]


@app.get(
    "/api/analysis/{analysis_id}/status",
    summary="Lightweight status check",
    tags=["Analysis"],
)
async def get_analysis_status(analysis_id: str):
    """Return just the status of an analysis — lightweight alternative to full result."""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")

    stored = analysis_store[analysis_id]
    return {
        "analysis_id": analysis_id,
        "status": stored.get("status", "unknown"),
        "filename": stored.get("filename", ""),
    }


@app.get(
    "/api/history",
    summary="List recent analyses",
    tags=["History"],
)
async def get_history(limit: int = 20):
    """
    Return the most recent analyses from Firestore.
    Results exclude the full `result` payload for efficiency.

    Falls back to in-memory store when Firestore is unavailable.
    """
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")

    if _firestore.is_available():
        return {"analyses": _firestore.list_recent_analyses(limit=limit)}

    # Fallback: summarize in-memory store
    summaries = [
        {
            "analysis_id": aid,
            "filename": data.get("filename", ""),
            "status": data.get("status", "unknown"),
        }
        for aid, data in list(analysis_store.items())[-limit:]
    ]
    return {"analyses": list(reversed(summaries))}


# ─────────────────────────────────────────
#  Text-to-Speech routes (Accessibility)
# ─────────────────────────────────────────

@app.get(
    "/api/tts/{analysis_id}/verdict",
    summary="TTS audio for the final verdict",
    tags=["Accessibility"],
    response_class=Response,
)
async def tts_verdict(analysis_id: str):
    """
    Returns MP3 audio of the one-liner verdict and executive summary.
    Supports screen readers and visually impaired users.
    """
    stored = analysis_store.get(analysis_id)
    if not stored or stored["status"] != "complete":
        raise HTTPException(status_code=404, detail="Analysis not complete")

    if not _tts.is_available():
        raise HTTPException(
            status_code=503,
            detail="Text-to-Speech service is not configured on this server",
        )

    result = stored["result"]
    try:
        audio_bytes = _tts.synthesize_verdict(
            verdict=result.get("one_liner_verdict", "Analysis complete."),
            summary=result.get("executive_summary", ""),
        )
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="verdict-{analysis_id[:8]}.mp3"',
                "Cache-Control": "public, max-age=3600",
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"TTS failed: {exc}") from exc


@app.get(
    "/api/tts/{analysis_id}/finding/{clause_id}",
    summary="TTS audio for a specific risk finding",
    tags=["Accessibility"],
    response_class=Response,
)
async def tts_finding(analysis_id: str, clause_id: str):
    """
    Returns MP3 audio for a specific risk finding identified by clause_id.
    Enables screen-reader-friendly contract review.
    """
    stored = analysis_store.get(analysis_id)
    if not stored or stored["status"] != "complete":
        raise HTTPException(status_code=404, detail="Analysis not complete")

    if not _tts.is_available():
        raise HTTPException(status_code=503, detail="TTS not configured")

    findings = stored["result"].get("findings", [])
    finding = next(
        (f for f in findings if f.get("clause_id") == clause_id), None
    )
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    try:
        audio_bytes = _tts.synthesize_finding(
            plain_explanation=finding.get("plain_explanation", ""),
            severity=finding.get("severity", "UNKNOWN"),
        )
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="finding-{clause_id}.mp3"',
                "Cache-Control": "public, max-age=3600",
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"TTS failed: {exc}") from exc


# ─────────────────────────────────────────
#  WebSocket
# ─────────────────────────────────────────

@app.websocket("/ws/analysis/{analysis_id}")
async def websocket_analysis(websocket: WebSocket, analysis_id: str):
    """
    Real-time WebSocket feed for live agent progress updates.
    Connect immediately after POST /api/analyze.
    Send 'ping' → receive {'type': 'pong'} for keepalive.
    """
    await websocket.accept()
    ws_connections[analysis_id] = websocket

    try:
        # If already complete, immediately send the completion event
        stored = analysis_store.get(analysis_id)
        if stored and stored["status"] == "complete":
            await websocket.send_json({
                "agent_name": "System",
                "status": "complete",
                "message": "Analysis already complete",
                "progress": 100,
                "findings_count": len(
                    stored.get("result", {}).get("findings", [])
                ),
                "analysis_id": analysis_id,
            })

        # Keep connection alive
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(), timeout=60.0
                )
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        logger.warning("[WS] Unexpected error for %s: %s", analysis_id, exc)
    finally:
        ws_connections.pop(analysis_id, None)


# ─────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENVIRONMENT", "development") == "development",
        log_level="info",
    )
