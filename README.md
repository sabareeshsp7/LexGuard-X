<div align="center">

# ⚖️ LexGuard X

### AI-Powered Contract Intelligence Platform

**Know your rights before you sign.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Vertex AI](https://img.shields.io/badge/Vertex%20AI-Gemini%202.0%20Flash%20Lite-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/vertex-ai)
[![CI](https://github.com/sabareeshsp7/LexGuard-X/actions/workflows/ci.yml/badge.svg)](https://github.com/sabareeshsp7/LexGuard-X/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## 📋 Table of Contents

1. [Challenge Vertical](#-challenge-vertical)
2. [Overview](#-overview)
3. [Approach & Logic](#-approach--logic)
4. [How the Solution Works](#-how-the-solution-works)
5. [Agent Pipeline](#-agent-pipeline)
6. [Google Services Integration](#-google-services-integration)
7. [Tech Stack](#-tech-stack)
8. [Project Structure](#-project-structure)
9. [Quick Start](#-quick-start)
10. [Environment Variables](#-environment-variables)
11. [API Reference](#-api-reference)
12. [Code Quality & Security](#-code-quality--security)
13. [Testing](#-testing)
14. [Accessibility](#-accessibility)
15. [Assumptions Made](#-assumptions-made)
16. [Deployment](#-deployment)
17. [License](#-license)

---

## 🎯 Challenge Vertical

**Vertical: Legal Tech / Smart Document Assistant**

LexGuard X is built for the **Legal Assistance** vertical. Millions of people sign contracts every day — employment agreements, rental leases, SaaS terms of service, NDAs, insurance policies — without understanding what they are agreeing to. Legal fees make professional review inaccessible to most individuals.

LexGuard X solves this by acting as a **smart, AI-powered legal assistant** that:
- Reads and understands any contract document using **Google Cloud Vision OCR**
- Makes **logical decisions** based on document context and contract type
- Identifies harmful clauses using **Vertex AI Gemini 3.1 Flash Lite**
- Enriches analysis with **Google Cloud Natural Language** entity extraction
- Persists every result in **Cloud Firestore** for history retrieval
- Reads findings aloud via **Google Cloud Text-to-Speech** for accessibility
- Logs every operation to **Google Cloud Logging** for audit trails

---

## 🌟 Overview

LexGuard X is a full-stack platform that gives everyday users the power of a senior contract attorney. Upload any legal document and a **pipeline of 8 specialized AI agents** powered by **Google Vertex AI Gemini 3.1 Flash Lite** will analyze it in real-time.

| Output | Description |
|---|---|
| **Contract Classification** | Automatically identifies document type |
| **Risk Score (0–100)** | Weighted danger score with 6-dimension breakdown |
| **Risk Findings** | Clause-level findings: CRITICAL / HIGH / MEDIUM / LOW |
| **Privacy Audit** | GDPR/CCPA compliance check |
| **Financial Traps** | Hidden fees, auto-renewals, penalty clauses |
| **Ambiguity Detection** | Vague language that could be used against you |
| **NLP Enrichment** | Named entities and content categories via Cloud NLP |
| **Future Scenarios** | Best-case, realistic, and worst-case outcomes |
| **Negotiation Advice** | Counter-clauses ready to send |
| **TTS Audio** | Every finding and verdict readable aloud |
| **One-Liner Verdict** | SIGN · NEGOTIATE · DO NOT SIGN · REVIEW WITH LAWYER |

All findings stream live via **WebSocket**. All results persist in **Firestore**.

---

## 🧠 Approach & Logic

### Design Philosophy

A **multi-agent reasoning pipeline** where each agent is a domain expert with a focused responsibility — mirroring how a real legal team operates.

### Decision-Making Logic

```
User Upload → OCR (Cloud Vision) → NLP Enrichment → RAG Chunking
→ Contract Classification → Domain Risk Agents → Weighted Scoring
→ Future Simulation → Negotiation Advice → Judge Verdict
→ Firestore Persistence → TTS Audio Output
```

**Step 1 — Document Ingestion (Cloud Vision + pypdf):**
Cloud Vision API performs OCR on scanned documents and images. Digital PDFs use pypdf directly. This ensures any contract — scanned, photographed, or digital — can be analyzed.

**Step 2 — NLP Enrichment (Cloud Natural Language):**
Before analysis begins, the Natural Language API extracts named entities (companies, monetary values, dates, legal terms) and analyzes sentiment. Negative sentiment in contract text often correlates with adversarial language.

**Step 3 — RAG Semantic Chunking (ChromaDB):**
Contract text is split into clause-aware chunks and stored with embeddings. Each specialized agent retrieves only the most relevant chunks via semantic similarity — reducing AI token usage by ~70%.

**Step 4 — Contract Classification (Vertex AI):**
Determines the contract type (Employment, NDA, SaaS, Rental, etc.) before risk analysis. This matters because risk thresholds differ: a non-compete is expected in employment but alarming in a SaaS agreement.

**Step 5 — Domain Risk Agents (Vertex AI × 4):**
Four specialist agents each scan for their domain: legal risks, privacy violations, financial traps, and ambiguous language.

**Step 6 — Deterministic Scoring (Python):**
A rule-based `RiskEngine` (no AI) calculates the final score using severity weights and category bonuses. This ensures consistent, reproducible, auditable scoring.

```
CRITICAL = 25 pts | HIGH = 15 pts | MEDIUM = 8 pts | LOW = 3 pts
IP_TRANSFER +10 | NON_COMPETE +8 | ARBITRATION +7 | PRIVACY +6
```

**Step 7 — Synthesis (Vertex AI):**
A "Judge Agent" synthesizes all findings into a plain-English executive summary and a single actionable verdict.

**Step 8 — Persistence & Accessibility:**
Results saved to **Firestore** for history retrieval. **Cloud TTS** generates MP3 audio of the verdict and each finding for visually impaired users. All events logged to **Cloud Logging**.

---

## ⚙️ How the Solution Works

### User Flow

```
1. User visits LexGuard X → drags and drops a contract file
2. POST /api/analyze → file validated, analysis_id returned
3. Browser connects WebSocket /ws/analysis/{id}
4. Cloud Vision OCR → NLP enrichment → RAG chunking
5. 8 AI agents run sequentially → live events streamed to UI
6. Results persisted to Firestore + GCS
7. Dashboard loads → Risk Radar, Clause Viewer, Negotiation Panel
8. User clicks 🔊 to hear findings via Cloud TTS
9. User revisits any past analysis via /api/history
```

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                         │
│   UploadZone → AgentFeed → RiskRadar → NegotiationPanel     │
│   ClauseViewer → 🔊 TTS Player                             │
└───────┬──────────────┬────────────────┬────────────────────┘
        │ HTTP POST    │ WebSocket      │ HTTP GET
┌───────▼──────────────▼────────────────▼────────────────────┐
│                    FastAPI Backend                          │
│                                                             │
│  POST /api/analyze     → Background analysis thread        │
│  WS   /ws/analysis/{id}← Live agent broadcast              │
│  GET  /api/analysis/{id}→ Full result                      │
│  GET  /api/history     → Firestore history                 │
│  GET  /api/tts/{id}/verdict   → MP3 audio                  │
│  GET  /api/tts/{id}/finding/{clause_id} → MP3 audio        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              CrewOrchestrator                        │  │
│  │  DocumentParser → RAGEngine → LegalAgents(×8)        │  │
│  │                             → RiskEngine             │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬────────────────────────────────────┘
                        │
        ┌───────────────┴──────────────────────────┐
        │           Google Cloud Platform           │
        │                                           │
        │  ┌─────────────┐  ┌──────────────────┐   │
        │  │  Vertex AI  │  │  Cloud Vision    │   │
        │  │Gemini 1.5Pro│  │  (OCR / images)  │   │
        │  └─────────────┘  └──────────────────┘   │
        │  ┌─────────────┐  ┌──────────────────┐   │
        │  │  Firestore  │  │  Cloud NLP       │   │
        │  │  (history)  │  │  (entities/NLP)  │   │
        │  └─────────────┘  └──────────────────┘   │
        │  ┌─────────────┐  ┌──────────────────┐   │
        │  │   Cloud     │  │  Cloud TTS       │   │
        │  │  Storage    │  │  (accessibility) │   │
        │  └─────────────┘  └──────────────────┘   │
        │  ┌─────────────┐                          │
        │  │   Cloud     │                          │
        │  │  Logging    │                          │
        │  └─────────────┘                          │
        └───────────────────────────────────────────┘
```

---

## 🤖 Agent Pipeline

| # | Agent | Role | Provider |
|---|---|---|---|
| — | **DocumentParser** | OCR + text extraction | Cloud Vision / pypdf / Azure |
| — | **NLP Enrichment** | Entity + sentiment analysis | Cloud Natural Language |
| — | **RAG Engine** | Semantic chunking + retrieval | ChromaDB + sentence-transformers |
| 1 | **Contract Classifier** | Identifies contract type | Vertex AI Gemini |
| 2 | **Legal Risk Analyst** | Exploitative clause detection | Vertex AI + RAG |
| 3 | **Privacy Agent** | GDPR/CCPA compliance | Vertex AI |
| 4 | **Financial Agent** | Hidden fees, auto-renewals | Vertex AI |
| 5 | **Ambiguity Detector** | Vague, undefined language | Vertex AI |
| — | **Risk Engine** | Weighted 0-100 scoring | Pure Python (deterministic) |
| 6 | **Future Simulator** | 3 real-world outcome scenarios | Vertex AI |
| 7 | **Negotiation Advisor** | Counter-clause drafting | Vertex AI |
| 8 | **Judge / Synthesizer** | Executive summary + verdict | Vertex AI |
| — | **TTS Output** | Audio for accessibility | Cloud Text-to-Speech |
| — | **Audit Logger** | Structured event logging | Cloud Logging |
| — | **History Store** | Result persistence | Cloud Firestore |

---

## ☁️ Google Services Integration

LexGuard X integrates **7 Google Cloud services** meaningfully — each one directly contributing to core functionality:

### 1. Vertex AI — Gemini 3.1 Flash Lite
Powers all 8 AI agents. Used for contract classification, risk detection, privacy audit, financial analysis, ambiguity detection, future simulation, negotiation advice, and verdict synthesis.

```python
vertexai.init(project=self.project_id, location=self.location)
self._model = GenerativeModel("gemini-2.0-flash-lite")
```
*Fallback:* Gemini API key via `google-genai` when Vertex credentials are unavailable.

### 2. Google Cloud Vision API
Primary OCR engine for all scanned documents and image-based contracts. Replaces external Azure dependency for image parsing, keeping the full processing pipeline on Google Cloud.

```python
response = client.document_text_detection(image=vision.Image(content=image_bytes))
full_text = response.full_text_annotation.text
```

### 3. Google Cloud Natural Language API
Enriches every analysis with:
- **Named entity extraction** — identifies parties, dates, monetary values, legal terms
- **Sentiment analysis** — negative sentiment score flags adversarial contract language
- **Content classification** — secondary contract-type verification

```python
response = client.analyze_entities(document=document)
response = client.analyze_sentiment(document=document)
```

### 4. Google Cloud Text-to-Speech (Accessibility)
Converts findings and verdicts to Neural2-quality MP3 audio. Served via dedicated `/api/tts/*` endpoints. Enables visually impaired users to hear every risk finding read aloud.

```python
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=0.95,
    effects_profile_id=["headphone-class-device"],
)
```

### 5. Google Cloud Firestore
Persists every analysis result for history retrieval. Provides durable storage so results survive server restarts. Powers the `/api/history` endpoint.

```python
db.collection("analyses").document(analysis_id).set(result_payload)
```

### 6. Google Cloud Storage
Stores original contract files and JSON reports in separate GCS buckets. Enables audit trails and future re-analysis without re-uploading.

```python
blob.upload_from_string(file_bytes, content_type="application/octet-stream")
```

### 7. Google Cloud Logging
Structured audit logging for every critical operation — uploads, analysis completions, errors, AI calls. Falls back to stdout when credentials are unavailable.

```python
cloud_logger.log_struct(payload, severity="INFO")
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Core language |
| FastAPI | 0.111 | REST API + WebSocket |
| Pydantic | v2 | Data validation |
| Uvicorn | 0.30 | ASGI server |
| google-cloud-aiplatform | 1.56 | Vertex AI SDK |
| google-genai | 1.0.0 | Gemini API fallback |
| google-cloud-vision | 3.7.2 | OCR for images/scanned PDFs |
| google-cloud-language | 2.13.4 | NLP entity + sentiment |
| google-cloud-texttospeech | 2.16.3 | TTS accessibility audio |
| google-cloud-firestore | 2.16.0 | Analysis history |
| google-cloud-storage | 2.17.0 | File + report persistence |
| google-cloud-logging | 3.10.0 | Structured audit logging |
| ChromaDB | 0.5.3 | Vector database for RAG |
| sentence-transformers | 3.0.1 | Embedding model |
| pypdf | 4.2.0 | Digital PDF parser |
| python-docx | 1.1.2 | DOCX parser |
| pytest | 8.2.2 | Test framework |
| httpx | 0.27.0 | Test HTTP client |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 19 | UI framework |
| TypeScript | 5.x | Type safety |
| Vite | 8 | Build tooling |
| Framer Motion | 12 | Animations |
| Recharts | 3 | Risk Radar visualization |
| Lucide React | 1 | Icons |
| React Dropzone | 15 | File upload |
| Axios | 1 | HTTP client |
| React Router | v7 | Routing |

---

## 📁 Project Structure

```
LexGuard-X/
│
├── backend/
│   ├── main.py                    # FastAPI app — all routes + WebSocket
│   ├── requirements.txt           # Pinned Python dependencies
│   ├── Dockerfile                 # Container definition
│   ├── pytest.ini                 # Test configuration
│   ├── .env.example               # Environment template (no secrets)
│   │
│   ├── agents/
│   │   ├── legal_agents.py        # 8 AI agent implementations
│   │   └── crew_orchestrator.py   # Sequential pipeline
│   │
│   ├── services/
│   │   ├── document_parser.py     # OCR: Cloud Vision → Azure → pypdf
│   │   ├── vision_client.py       # Google Cloud Vision API
│   │   ├── nlp_client.py          # Google Cloud Natural Language API
│   │   ├── tts_client.py          # Google Cloud Text-to-Speech API
│   │   ├── firestore_client.py    # Google Cloud Firestore
│   │   ├── storage_client.py      # Google Cloud Storage
│   │   ├── logging_client.py      # Google Cloud Logging
│   │   ├── rag_engine.py          # ChromaDB + embeddings
│   │   ├── risk_engine.py         # Deterministic risk scoring
│   │   └── vertex_client.py       # Vertex AI / Gemini client
│   │
│   ├── models/
│   │   └── schemas.py             # Pydantic v2 data models
│   │
│   ├── tests/
│   │   ├── test_api.py            # FastAPI endpoint tests
│   │   ├── test_risk_engine.py    # Risk scoring unit tests
│   │   ├── test_schemas.py        # Pydantic validation tests
│   │   ├── test_rag_engine.py     # Chunking logic tests
│   │   └── test_document_parser.py# Parser + fallback chain tests
│   │
│   └── uploads/                   # Runtime uploads (gitignored)
│
├── frontend/
│   ├── index.html                 # HTML entry + SEO meta
│   └── src/
│       ├── App.tsx                # Router
│       ├── pages/Home.tsx         # Upload page
│       ├── pages/Analysis.tsx     # Results dashboard
│       └── components/
│           ├── UploadZone.tsx     # Drag & drop upload
│           ├── AgentFeed.tsx      # Live WebSocket feed
│           ├── RiskRadar.tsx      # Radar chart
│           ├── ClauseViewer.tsx   # Findings explorer
│           └── NegotiationPanel.tsx
│
├── .gitignore
├── README.md
└── LICENSE
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+, Node.js 20+, npm
- Google Cloud account (or free [Gemini API Key](https://aistudio.google.com/app/apikey))

### Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env — minimum: set GEMINI_API_KEY

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> API: `http://localhost:8000` | Swagger: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

> UI: `http://localhost:5173`

---

## 🔑 Environment Variables

> ⚠️ **Never commit `.env` or `gcp-key.json`** — both are in `.gitignore`

### Minimum Required (pick one):

**Option A — Gemini API Key (free, easiest):**
```env
GEMINI_API_KEY=your-gemini-api-key-here
```

**Option B — Vertex AI (GCP credits, unlocks ALL Google services):**
```env
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
VERTEX_MODEL=gemini-3.1-flash-lite
```

> With `GCP_PROJECT_ID` + `gcp-key.json`, all 7 Google services activate automatically:
> Cloud Vision, Natural Language, Text-to-Speech, Firestore, Storage, Logging, Vertex AI.

### Live Deployment
| Environment | URL |
|---|---|
| 🌐 Frontend | https://connect-7sp.web.app |
| ⚙️ Backend API | https://lexguard-backend-tvdarg3hea-uc.a.run.app |
| 📖 API Docs | https://lexguard-backend-tvdarg3hea-uc.a.run.app/docs |

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health + Google service status |
| `POST` | `/api/analyze` | Upload contract, start analysis |
| `GET` | `/api/analysis/{id}` | Full analysis result |
| `GET` | `/api/analysis/{id}/status` | Lightweight status check |
| `GET` | `/api/history` | Recent analyses from Firestore |
| `GET` | `/api/tts/{id}/verdict` | MP3 audio of verdict |
| `GET` | `/api/tts/{id}/finding/{clause_id}` | MP3 audio of a finding |
| `WS` | `/ws/analysis/{id}` | Real-time agent progress feed |

### File Upload Constraints
- Formats: `.pdf`, `.docx`, `.doc`, `.png`, `.jpg`, `.jpeg`, `.tiff`
- Max size: **20 MB**

### WebSocket Event Format
```json
{
  "agent_name": "Legal Risk Agent",
  "status": "running",
  "message": "Scanning for harmful clauses...",
  "progress": 20,
  "findings_count": 3
}
```

---

## 🔒 Code Quality & Security

### Code Quality
- **Typed throughout:** Pydantic v2 models for all I/O; TypeScript strict mode frontend
- **Separation of concerns:** Each Google service in its own `services/` module
- **Lazy initialization:** All clients initialize on first use — no startup overhead
- **Graceful degradation:** Every service has a safe no-op fallback
- **Consistent error handling:** Errors caught per agent; pipeline never crashes
- **Structured logging:** `CloudLogger` used throughout with severity tags

### Security
- **No secrets in source:** All credentials loaded from `.env` via `python-dotenv`
- **`.env` and `gcp-key.json` gitignored** at root level
- **File type allowlist:** Only whitelisted extensions processed
- **File size cap:** 20 MB enforced server-side (returns HTTP 413)
- **Restrictive CORS:** Configurable via `ALLOWED_ORIGINS` env var
- **Input validation:** All parameters validated before processing

### Efficiency
- **RAG retrieval:** Agents query relevant chunks only — ~70% fewer tokens
- **NLP enrichment:** Runs once per document; results attached to payload
- **Batch embeddings:** `sentence-transformers` encodes in batches of 32
- **Deterministic scoring:** Risk calculation uses no AI — pure Python math
- **Lazy loading:** All heavy clients initialized on first call
- **Background threads:** Analysis never blocks the HTTP server

---

## 🧪 Testing

```bash
cd backend
pip install pytest pytest-asyncio httpx
pytest tests/ -v
```

### Test Files

| File | Coverage |
|---|---|
| `test_risk_engine.py` | 20+ tests: scoring, thresholds, dimensions, labels, prioritization |
| `test_schemas.py` | Pydantic validation for all models, boundary values, required fields |
| `test_rag_engine.py` | Chunking: clause-aware, sliding window, overlap, size limits |
| `test_document_parser.py` | Extension validation, fallback chain, Cloud Vision mock, pypdf |
| `test_api.py` | All HTTP endpoints: health, upload, result, history, TTS, status codes |

### Manual Testing Checklist
```
☑ Upload PDF → analysis_id returned
☑ WebSocket → live agent events stream
☑ Wait → GET /api/analysis/{id} → full result
☑ GET /api/history → shows recent analyses
☑ GET /api/tts/{id}/verdict → downloads MP3
☑ Upload .xlsx → 400 error
☑ Upload empty file → 400 error
☑ Upload > 20MB → 413 error
☑ GET unknown analysis → 404 error
☑ WebSocket ping → pong response
```

---

## ♿ Accessibility

- **Semantic HTML:** Proper `<main>`, `<section>`, `<article>`, heading hierarchy
- **ARIA labels:** All interactive elements labeled for screen readers
- **`aria-live="polite"`:** WebSocket updates announced to assistive tech
- **Keyboard navigation:** Full keyboard operability — no mouse required
- **WCAG 2.1 AA contrast:** All text meets 4.5:1 minimum contrast ratio
- **Visible focus rings:** Clear focus indicators on all interactive elements
- **`prefers-reduced-motion`:** Animations disabled for users who prefer it
- **Responsive design:** Usable on 320px+ mobile through desktop
- **🔊 Cloud TTS Audio:** Every risk finding and the final verdict can be heard aloud via `/api/tts/*` endpoints — designed specifically for visually impaired users
- **Plain English output:** All AI findings written in non-legal language

---

## 📐 Assumptions Made

1. **Single-instance deployment:** `analysis_store` is in-memory; Firestore is the durable backing store. For multi-instance, add Redis.
2. **Sequential agent pipeline:** Agents run one-by-one to respect Vertex AI quota and maintain logical event order.
3. **English-language contracts:** Prompts are optimized for English. Other languages may work but are not guaranteed.
4. **User is the non-drafting party:** All agents advocate for the user — not the company or employer.
5. **20 MB file limit:** Covers all real-world text-based legal documents.
6. **ChromaDB is per-process:** For multi-instance production, replace with Vertex AI Matching Engine.
7. **GCS optional:** Without GCS credentials, files process in-memory and results stay in Firestore only.
8. **Gemini API key = development mode:** Full Google Cloud service stack requires `gcp-key.json` + `GCP_PROJECT_ID`.

---

## 🐳 Deployment

### Docker (Backend)
```bash
cd backend
docker build -t lexguard-backend .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your-key \
  -e GCP_PROJECT_ID=your-project \
  -v $(pwd)/gcp-key.json:/app/gcp-key.json \
  lexguard-backend
```

### Frontend
```bash
cd frontend
npm run build
# Serve dist/ on Firebase Hosting, Vercel, or Netlify
```

### Google Cloud Run (Recommended)
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT/lexguard-backend
gcloud run deploy lexguard-backend \
  --image gcr.io/YOUR_PROJECT/lexguard-backend \
  --platform managed --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=your-project,GEMINI_API_KEY=your-key
```

### Production Stack
| Component | Service | URL |
|---|---|---|
| Backend | Google Cloud Run | https://lexguard-backend-tvdarg3hea-uc.a.run.app |
| Frontend | Firebase Hosting | https://connect-7sp.web.app |
| AI | Vertex AI Gemini 2.0 Flash Lite | us-central1 |
| OCR | Cloud Vision API | us-central1 |
| NLP | Cloud Natural Language | us-central1 |
| TTS | Cloud Text-to-Speech | us-central1 |
| History | Cloud Firestore | us-central1 |
| Files | Cloud Storage | lexguard-contracts-bucket |
| Logs | Cloud Logging | connect-7sp project |
| CI/CD | GitHub Actions + Cloud Build | `.github/workflows/ci.yml` |

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

<div align="center">

**7 Google Cloud Services · FastAPI · React · TypeScript**

**LexGuard X** — *Smart contract intelligence for everyone.*

⭐ Star this repo if it helped you!

</div>
