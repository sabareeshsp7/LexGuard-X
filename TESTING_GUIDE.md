# LexGuard X: Comprehensive Testing Guide

This guide provides a detailed, step-by-step approach to testing the LexGuard X platform. It covers automated unit testing, manual end-to-end (E2E) testing, Google Cloud service verification, and edge-case handling.

---

## 1. Prerequisites for Testing

Before you begin testing, ensure your local environment is correctly configured:

1. **Python Environment:** Ensure you are using Python 3.11+.
2. **Virtual Environment Active:** 
   ```bash
   cd backend
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. **Environment Variables:**
   Ensure your `.env` file in the `backend/` directory is properly filled out. For full testing, you should have `GCP_PROJECT_ID` and `GOOGLE_APPLICATION_CREDENTIALS` set, along with your `VERTEX_MODEL` set to `gemini-3.1-flash-lite`.
4. **Dependencies Installed:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 2. Automated Testing (Backend)

LexGuard X uses `pytest` for automated backend testing. The test suite is designed to run without making live calls to Google Cloud or Vertex AI (services are mocked) to ensure they are fast, reliable, and free to run.

### Running the Test Suite
From the `backend/` directory, run:
```bash
pytest tests/ -v
```

### What the Automated Tests Cover:

1. **`test_api.py` (API Endpoints):**
   - Tests all FastAPI routes (`/api/health`, `/api/analyze`, `/api/history`, etc.).
   - Verifies HTTP status codes (200 OK, 400 Bad Request, 404 Not Found, 413 Payload Too Large).
   - Simulates file uploads and validates that unsupported extensions are rejected.

2. **`test_risk_engine.py` (Deterministic Math):**
   - Tests the pure-Python scoring logic.
   - Verifies that scoring caps out at 100 and cannot be negative.
   - Ensures correct severity labels (LOW, MEDIUM, HIGH, CRITICAL) are assigned based on the calculated score.
   - Tests that findings are correctly prioritized (Critical findings sorted to the top).

3. **`test_schemas.py` (Data Validation):**
   - Validates that Pydantic models correctly enforce data constraints.
   - Ensures impact scores fall between 0.0 and 10.0.
   - Verifies required fields cannot be bypassed.

4. **`test_rag_engine.py` (Text Chunking):**
   - Tests the sliding-window text chunker.
   - Ensures chunks do not exceed the `MAX_CHUNK_SIZE`.
   - Validates that overlapping characters are properly carried over between chunks.

5. **`test_document_parser.py` (Extraction Logic):**
   - Verifies the fallback logic (e.g., if pypdf fails or extracts too little text, it falls back to Cloud Vision).
   - Validates file extension checks.

---

## 3. Manual End-to-End (E2E) Testing

Manual testing ensures the frontend and backend communicate correctly over HTTP and WebSockets.

### Step 3.1: Start the Servers
**Backend (Terminal 1):**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

### Step 3.2: The Happy Path (Standard Usage)
1. Open your browser to `http://localhost:5173`.
2. Click the upload zone and select a standard valid PDF contract (e.g., an NDA or Employment Agreement).
3. **Verify Upload:** Ensure the file uploads successfully.
4. **Verify WebSocket:** You should see a live feed of agents updating their statuses ("Extracting text...", "Classifying contract...", "Scanning for risks...").
5. **Verify Dashboard:** Once complete, the Risk Radar chart, Clause Viewer, and Negotiation Panel should populate with data.
6. **Verify TTS:** Click the 🔊 (speaker) icon next to a finding or the final verdict to ensure the audio plays correctly.

### Step 3.3: Testing Edge Cases and Errors
1. **Empty File:** Create an empty `.pdf` file (0 bytes) and upload it. 
   * *Expected Result:* The frontend should display a user-friendly error, and the backend should return a 400 status code.
2. **Unsupported Format:** Try uploading an `.xlsx` or `.exe` file.
   * *Expected Result:* Immediate rejection by the file picker, or a 400 error from the backend.
3. **Massive File:** Try uploading a PDF larger than 20MB.
   * *Expected Result:* The backend should reject it with a 413 Payload Too Large error.
4. **Scanned Image / Photo:** Upload a `.jpg` or `.png` of a contract page.
   * *Expected Result:* The system should successfully route the file to Google Cloud Vision OCR, extract the text, and complete the analysis.

---

## 4. Verifying Google Cloud Integrations

To ensure your GCP setup is flawless, check the following during or after a live analysis:

1. **Cloud Vision API:** Upload an image (`.jpg`). Check your terminal logs. You should see `[Vision] OCR extracted X characters`.
2. **Cloud Natural Language API:** Check the terminal logs for `[NLP] X entities extracted, sentiment=Y`. The dashboard payload should also contain the `nlp_entities` list.
3. **Cloud Text-to-Speech:** Click the Audio button on the UI. The browser should download/play an `.mp3` file. If TTS is disabled, the API returns a 503 error.
4. **Cloud Firestore:** 
   - Refresh the page and check the `/api/history` route or the History UI tab.
   - Alternatively, log into the Google Cloud Console, navigate to Firestore, and check the `analyses` collection for your recent document.
5. **Cloud Storage:** Check your Google Cloud Console Storage Buckets. You should see the raw PDF and the `.json` report saved.
6. **Cloud Logging:** Navigate to the Logs Explorer in the Google Cloud Console. Search for `jsonPayload.service="lexguard-x"`. You should see structured logs for uploads and completed analyses.

---

## 5. Performance and Resilience Testing

1. **Concurrent Users:** 
   Open 3 different browser tabs and upload 3 different contracts simultaneously.
   * *Expected Result:* The backend threads should handle the analyses independently. WebSockets should route the correct messages to the correct tabs based on their unique `analysis_id`.
2. **AI Fallback Test:** 
   If you want to test how the system behaves without Vertex AI:
   - Temporarily remove `GOOGLE_APPLICATION_CREDENTIALS` from your `.env`.
   - Ensure `GEMINI_API_KEY` is set.
   - Restart the server and run an analysis.
   * *Expected Result:* Cloud Vision, Firestore, and TTS will gracefully degrade (skip or mock), and the core AI will use the free Gemini API Key instead of Vertex. The system should not crash.

---

## 6. Testing Checklist Summary

- [ ] `pytest tests/` passes 100%
- [ ] Standard PDF uploads and analyzes successfully
- [ ] Image (JPG/PNG) contract uploads and parses via OCR
- [ ] Live WebSocket agent updates appear on the frontend
- [ ] Risk Radar chart renders correctly
- [ ] Text-to-Speech audio plays for findings
- [ ] History endpoint retrieves past analyses from Firestore
- [ ] Uploading an unsupported file type fails gracefully
- [ ] Uploading a >20MB file fails gracefully
- [ ] Cloud Console shows logs in Logging Explorer

By following this guide, you can ensure that LexGuard X is robust, accessible, and fully integrated with the Google Cloud ecosystem.
