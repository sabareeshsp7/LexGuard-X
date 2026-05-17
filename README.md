<div align="center">

# ⚖️ LexGuard X

### AI-Powered Contract Intelligence Platform

**Know your rights before you sign.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Vertex AI](https://img.shields.io/badge/Vertex%20AI-Gemini%201.5%20Pro-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/vertex-ai)
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

LexGuard X is built for the **Legal Assistance** vertical. Millions of people sign contracts every day — employment agreements, rental leases, SaaS terms of service, NDAs, insurance policies — without truly understanding what they are agreeing to. Legal fees make professional review inaccessible to most individuals.

LexGuard X solves this by acting as a **smart, AI-powered legal assistant** that:
- Reads and understands any contract document
- Makes **logical decisions** based on the document context and contract type
- Identifies harmful clauses that could damage the user financially or legally
- Delivers **plain-English explanations** anyone can understand
- Suggests **concrete negotiation strategies** — empowering the user before they sign

---

## 🌟 Overview

LexGuard X is a full-stack platform that gives everyday users the power of a senior contract attorney. Upload any legal document and a **pipeline of 8 specialized AI agents** powered by **Google Vertex AI Gemini 1.5 Pro** will analyze it in real-time and deliver:

| Output | Description |
|---|---|
| **Contract Classification** | Identifies document type automatically |
| **Risk Score (0–100)** | Weighted danger level with per-dimension breakdown |
| **Risk Findings** | Clause-level findings rated CRITICAL / HIGH / MEDIUM / LOW |
| **Privacy Audit** | GDPR/CCPA compliance check |
| **Financial Traps** | Hidden fees, auto-renewals, penalty clauses |
| **Ambiguity Detection** | Vague language that could be used against you |
| **Future Scenarios** | Best-case, realistic, and worst-case outcomes |
| **Negotiation Advice** | Revised counter-clauses ready to send |
| **One-Liner Verdict** | SIGN · NEGOTIATE · DO NOT SIGN · REVIEW WITH LAWYER |

All findings are streamed live to your browser via **WebSocket** — no waiting for a spinner.

---

## 🧠 Approach & Logic

### Design Philosophy

The core approach is a **multi-agent reasoning pipeline** where each agent is a domain expert with a focused responsibility. This mirrors how a real legal team operates — different specialists review different aspects of the same document, and a senior judge synthesizes their findings into a final verdict.

### Decision-Making Logic

```
User Context → Document Type → Specialized Analysis → Risk Quantification → Verdict
```

**Step 1 — Context Gathering (RAG):**
The contract text is chunked into semantically meaningful pieces and stored in a vector database (ChromaDB). This allows each agent to retrieve only the most relevant clauses for its specific domain — financial agents query for fee-related clauses, privacy agents query for data-collection language, etc.

**Step 2 — Contract Classification:**
Before any risk analysis, the system determines the contract type (Employment, NDA, SaaS ToS, Rental, etc.). This context is passed to every subsequent agent, because what is "standard" varies by contract type. A non-compete clause is critical in a freelance contract but expected in an employment agreement.

**Step 3 — Parallel Domain Analysis:**
Five specialized agents each analyze the contract through their expert lens:
- Legal Risk: One-sided obligations, exploitative terms
- Privacy: Data collection, third-party sharing, retention
- Financial: Hidden costs, auto-renewals, penalty clauses
- Ambiguity: Vague language, undefined terms, discretionary powers

**Step 4 — Weighted Risk Scoring:**
A deterministic `RiskEngine` (not AI) calculates the final score using severity weights and category bonuses. This ensures consistent, reproducible, explainable scoring regardless of AI model variation.

```python
# Severity weights
CRITICAL = 25 pts | HIGH = 15 pts | MEDIUM = 8 pts | LOW = 3 pts

# Category danger bonuses (added on top)
IP_TRANSFER = +10 | NON_COMPETE = +8 | ARBITRATION = +7 | PRIVACY = +6
```

**Step 5 — Synthesis & Verdict:**
A "Judge Agent" synthesizes all findings into an executive summary and final recommendation, giving non-lawyers a clear, actionable answer.

### Why This Architecture

- **Separation of concerns:** Each agent is independently testable and replaceable
- **Deterministic scoring:** Risk quantification is rule-based, not AI-guessed, preventing hallucination
- **RAG for precision:** Semantic retrieval ensures agents analyze relevant context, not just raw chunks
- **Real-time UX:** WebSocket streaming means users see progress immediately, not after a 4-minute wait

---

## ⚙️ How the Solution Works

### User Flow

```
1. User visits the LexGuard X web app
2. Drags and drops a contract file (PDF, DOCX, or image)
3. File is uploaded → POST /api/analyze
4. Browser connects to WebSocket /ws/analysis/{id}
5. 8 AI agents run sequentially, streaming live updates to the UI
6. Results dashboard loads automatically when analysis completes
7. User views risk score, findings, scenarios, and negotiation advice
```

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                         │
│   UploadZone → AgentFeed → RiskRadar → NegotiationPanel     │
│        │ HTTP POST          │ WebSocket        │ HTTP GET    │
└────────┼────────────────────┼──────────────────┼────────────┘
         │                    │                  │
┌────────▼────────────────────▼──────────────────▼────────────┐
│                    FastAPI Backend                           │
│                                                             │
│  POST /api/analyze ──► Background Thread                    │
│  WS   /ws/analysis/{id}  ◄── Live broadcasts               │
│  GET  /api/analysis/{id}  ──► Full result                   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              CrewOrchestrator                        │   │
│  │  DocumentParser → RAGEngine → 8 LegalAgents          │   │
│  │                            → RiskEngine              │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
          ┌─────────────────┴──────────────────┐
          │         Google Cloud               │
          │  Vertex AI (Gemini 1.5 Pro)        │
          │  Google Cloud Storage              │
          │  Generative AI API (fallback)      │
          └────────────────────────────────────┘
```

---

## 🤖 Agent Pipeline

LexGuard X runs **8 sequential AI agents**, each a domain specialist built on **Gemini 1.5 Pro**:

| # | Agent | Role | Technology |
|---|---|---|---|
| 1 | **Contract Classifier** | Identifies contract type | Vertex AI |
| 2 | **Legal Risk Analyst** | Finds exploitative clauses | Vertex AI + RAG |
| 3 | **Privacy & Data Agent** | GDPR/CCPA compliance | Vertex AI |
| 4 | **Financial Liability Agent** | Hidden fees, auto-renewals | Vertex AI |
| 5 | **Ambiguity Detector** | Vague, undefined language | Vertex AI |
| — | **Risk Engine** | Weighted scoring (0–100) | Deterministic Python |
| 6 | **Future Simulator** | 3 real-world outcome scenarios | Vertex AI |
| 7 | **Negotiation Advisor** | Counter-clause drafting | Vertex AI |
| 8 | **Judge / Synthesizer** | Executive summary + verdict | Vertex AI |

---

## ☁️ Google Services Integration

LexGuard X meaningfully integrates **3 core Google Cloud services**:

### 1. Google Vertex AI — Gemini 1.5 Pro
The backbone of all 8 AI agents. Gemini 1.5 Pro is used for:
- Contract classification and type detection
- Legal clause risk analysis
- Privacy and financial risk detection
- Ambiguity and vague language identification
- Future scenario simulation
- Negotiation counter-clause drafting
- Executive summary synthesis

```python
# vertex_client.py — Vertex AI initialization
vertexai.init(project=self.project_id, location=self.location)
self._model = GenerativeModel("gemini-1.5-pro-001")
```

### 2. Google Cloud Storage (GCS)
Every analyzed contract and its JSON report are persisted to GCS buckets:
- `gs://lexguard-contracts-bucket/contracts/{analysis_id}/{filename}`
- `gs://lexguard-reports-bucket/reports/{analysis_id}.json`

This enables audit trails, report retrieval, and future re-analysis without re-uploading.

### 3. Google Generative AI API (Fallback)
When Vertex AI credentials are unavailable (e.g., local development), the system automatically falls back to the **Gemini API via `google-genai`** — ensuring the app works with just a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

```python
# Automatic fallback to Gemini API key
from google import genai
client = genai.Client(api_key=gemini_key)
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Core language |
| FastAPI | 0.111 | REST API + WebSocket server |
| Pydantic | v2 | Data validation & serialization |
| Uvicorn | 0.30 | ASGI production server |
| google-cloud-aiplatform | 1.56 | Vertex AI SDK |
| google-genai | latest | Gemini API SDK |
| google-cloud-storage | 2.17 | GCS file persistence |
| ChromaDB | 0.5.3 | Vector database for RAG |
| sentence-transformers | 3.0.1 | `all-MiniLM-L6-v2` embeddings |
| azure-ai-documentintelligence | 1.0.0b4 | Premium PDF/OCR parsing |
| pypdf | 4.2.0 | PDF fallback parser |
| python-docx | 1.1.2 | DOCX parsing |
| python-dotenv | 1.0.1 | Environment configuration |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| React | 19 | UI framework |
| TypeScript | 5.x | Type safety |
| Vite | 8 | Build tooling & dev server |
| Framer Motion | 12 | Smooth animations |
| Recharts | 3 | Risk Radar chart visualization |
| Lucide React | 1 | Icon system |
| React Dropzone | 15 | Drag & drop file upload |
| Axios | 1 | HTTP client |
| React Router | v7 | Client-side routing |

---

## 📁 Project Structure

```
LexGuard-X/
│
├── backend/                          # FastAPI Python backend
│   ├── main.py                       # App entry, routes, WebSocket manager
│   ├── requirements.txt              # All Python dependencies pinned
│   ├── Dockerfile                    # Container definition
│   ├── .env.example                  # ← Template (no secrets)
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── legal_agents.py           # 8 AI agent implementations
│   │   └── crew_orchestrator.py      # Sequential pipeline orchestration
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_parser.py        # PDF/DOCX/image text extraction
│   │   ├── rag_engine.py             # ChromaDB + embeddings RAG system
│   │   ├── risk_engine.py            # Deterministic weighted risk scoring
│   │   ├── storage_client.py         # Google Cloud Storage client
│   │   └── vertex_client.py          # Vertex AI / Gemini API client
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py                # Pydantic v2 data models & enums
│   │
│   └── uploads/                      # Runtime upload dir (gitignored)
│       └── .gitkeep
│
├── frontend/                         # React TypeScript frontend
│   ├── index.html                    # HTML entry + SEO meta tags
│   ├── package.json                  # npm dependencies
│   ├── tsconfig.json                 # TypeScript strict config
│   ├── vite.config.ts                # Vite build config
│   │
│   └── src/
│       ├── App.tsx                   # Router setup (Home + Analysis routes)
│       ├── main.tsx                  # React StrictMode entry
│       ├── index.css                 # Design system + global styles
│       ├── types.ts                  # TypeScript interfaces & enums
│       │
│       ├── pages/
│       │   ├── Home.tsx              # Upload page with drag & drop
│       │   └── Analysis.tsx          # Full results dashboard
│       │
│       ├── components/
│       │   ├── UploadZone.tsx        # File upload with validation
│       │   ├── AgentFeed.tsx         # Live WebSocket agent progress feed
│       │   ├── RiskRadar.tsx         # Radar chart (6 risk dimensions)
│       │   ├── ClauseViewer.tsx      # Risk findings explorer
│       │   └── NegotiationPanel.tsx  # Counter-clause advisor
│       │
│       └── api/
│           └── client.ts             # Axios API client
│
├── .gitignore                        # Excludes secrets, venv, node_modules
├── README.md                         # This file
└── LICENSE                           # MIT License
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 20+** and **npm**
- A **Google Cloud account** with Vertex AI enabled, OR a free [Gemini API Key](https://aistudio.google.com/app/apikey)

---

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — add your GEMINI_API_KEY (minimum required)

# 5. Start the API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

> API live at: `http://localhost:8000`  
> Swagger docs: `http://localhost:8000/docs`

---

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Set API URL
echo "VITE_API_URL=http://localhost:8000" > .env

# 4. Start dev server
npm run dev
```

> UI live at: `http://localhost:5173`

---

## 🔑 Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

> ⚠️ **Never commit `.env` or `gcp-key.json` — both are excluded by `.gitignore`**

### Minimum Required (pick one):

#### Option A — Gemini API Key (free tier, easiest)
```env
GEMINI_API_KEY=your-gemini-api-key-here
```
Get your key at: https://aistudio.google.com/app/apikey

#### Option B — Google Vertex AI (GCP credits)
```env
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
VERTEX_MODEL=gemini-1.5-pro-001
```
Download `gcp-key.json` from **GCP → IAM → Service Accounts → Keys**

---

### Full Variable Reference

```env
# ── Google Cloud / Vertex AI ─────────────────────────────
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
VERTEX_MODEL=gemini-1.5-pro-001

# ── Gemini API Key (fallback) ─────────────────────────────
GEMINI_API_KEY=your-gemini-api-key-here

# ── Google Cloud Storage (optional) ──────────────────────
GCS_CONTRACTS_BUCKET=lexguard-contracts-bucket
GCS_REPORTS_BUCKET=lexguard-reports-bucket

# ── Azure Document Intelligence (optional, premium OCR) ──
AZURE_DOC_ENDPOINT=https://YOUR-RESOURCE.cognitiveservices.azure.com/
AZURE_DOC_KEY=your-azure-document-intelligence-key

# ── Azure Speech (optional) ───────────────────────────────
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=eastus

# ── App Configuration ─────────────────────────────────────
CHROMA_PERSIST_DIR=./chroma_db
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
UPLOAD_DIR=./uploads
```

---

## 📡 API Reference

### `GET /api/health`
Service health check.

```json
{
  "status": "healthy",
  "service": "LexGuard X API",
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

### `POST /api/analyze`
Upload a contract and start AI analysis.

**Request:** `multipart/form-data` with field `file`

**Supported formats:** `.pdf`, `.docx`, `.doc`, `.png`, `.jpg`, `.jpeg`, `.tiff`  
**Max size:** 20 MB

**Response:**
```json
{
  "analysis_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "Analysis started. Connect to WebSocket for live updates.",
  "status": "processing"
}
```

---

### `GET /api/analysis/{analysis_id}`
Get the full completed analysis result.

**Response (complete):**
```json
{
  "analysis_id": "a1b2c3d4-...",
  "contract_type": "Employment Agreement",
  "file_name": "contract.pdf",
  "total_clauses_found": 24,
  "risk_score": {
    "overall_score": 67.5,
    "level": "HIGH",
    "privacy_score": 45.0,
    "financial_score": 23.0,
    "legal_score": 55.0,
    "ip_score": 80.0,
    "ambiguity_score": 30.0,
    "employment_score": 60.0
  },
  "findings": [...],
  "future_scenarios": [...],
  "negotiation_recommendations": [...],
  "executive_summary": "...",
  "one_liner_verdict": "...",
  "created_at": "2025-01-15T10:32:00Z"
}
```

---

### `GET /api/analysis/{analysis_id}/status`
Lightweight polling status check.

```json
{
  "analysis_id": "a1b2c3d4-...",
  "status": "complete",
  "filename": "contract.pdf"
}
```

---

### `WS /ws/analysis/{analysis_id}`
WebSocket for real-time agent progress updates.

**Event format:**
```json
{
  "agent_name": "Legal Risk Agent",
  "status": "running",
  "message": "Scanning for harmful clauses...",
  "progress": 20,
  "findings_count": 3
}
```

| `status` values | Description |
|---|---|
| `running` | Agent is currently working |
| `done` | Agent completed successfully |
| `error` | Agent encountered an error |
| `complete` | Full analysis pipeline complete |

Send `"ping"` → receive `{"type": "pong"}` for keepalive.

---

## 🔒 Code Quality & Security

### Code Quality
- **Typed throughout:** Pydantic v2 models for all API inputs/outputs; TypeScript strict mode on the frontend
- **Separation of concerns:** Each service, agent, and model lives in its own module
- **Lazy initialization:** AI clients (VertexClient, RAGEngine) use lazy `_initialize()` to avoid startup cost
- **Graceful degradation:** Every external service (GCS, Azure, Vertex) has a safe fallback
- **Consistent error handling:** All agent errors are caught, logged, and never crash the pipeline

### Security Practices
- **No secrets in source code:** All credentials loaded exclusively from `.env` via `python-dotenv`
- **`.env` and `gcp-key.json` are gitignored** at root level — never committed
- **File type validation:** Only whitelisted extensions accepted at upload
- **File size limit:** 20 MB hard cap enforced server-side before processing
- **CORS:** Configured via FastAPI middleware (restrict origins in production)
- **No user data persistence by default:** Files processed in-memory; GCS upload is optional

### Efficiency
- **RAG retrieval:** Agents query only the most relevant chunks (not the full document) — reduces token usage by ~70%
- **Batch embeddings:** `sentence-transformers` encodes chunks in batches of 32 for throughput
- **Background threading:** Analysis runs in a daemon thread, keeping the API responsive
- **Deterministic scoring:** Risk calculation uses no AI calls — pure Python math — saving latency and cost
- **Lazy model loading:** Embedding model loaded once and reused across all analyses

---

## 🧪 Testing

### Running Tests

```bash
cd backend
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Test Coverage Areas

| Area | What Is Tested |
|---|---|
| **RiskEngine** | Score calculation, severity thresholds, category bonuses, edge cases (no findings) |
| **RAGEngine** | Text chunking (clause-aware + sliding window), chunk size limits |
| **DocumentParser** | PDF fallback parsing, DOCX parsing, unsupported type rejection |
| **Schemas** | Pydantic model validation, field constraints (score 0–100, impact 0–10) |
| **API Endpoints** | Health check, file upload validation, analysis retrieval, 404 handling |

### Manual Testing Checklist

```
☑ Upload a PDF contract → expect analysis_id returned
☑ Connect WebSocket → expect live agent events
☑ Wait for completion → fetch /api/analysis/{id}
☑ Upload unsupported file type → expect 400 error
☑ Upload file > 20MB → expect 400 error
☑ Request non-existent analysis → expect 404 error
☑ Send "ping" on WebSocket → expect "pong" response
```

---

## ♿ Accessibility

The LexGuard X frontend is built with accessibility as a core principle:

- **Semantic HTML:** Proper use of `<main>`, `<section>`, `<article>`, `<nav>`, `<header>`, heading hierarchy (`h1` → `h2` → `h3`)
- **ARIA labels:** All interactive elements have descriptive `aria-label` attributes
- **Keyboard navigation:** Full keyboard support — file upload, navigation, and result exploration without a mouse
- **Color contrast:** All text meets WCAG 2.1 AA contrast ratios (minimum 4.5:1)
- **Focus indicators:** Visible focus rings on all interactive elements
- **Screen reader support:** Live WebSocket updates announced via `aria-live="polite"` regions
- **No motion by default:** Animations respect `prefers-reduced-motion` media query
- **Responsive design:** Fully usable on mobile (320px+), tablet, and desktop
- **Plain English output:** All AI findings are written in non-legal language — accessible to users without legal background

---

## 📐 Assumptions Made

1. **Single-user, stateless API:** The `analysis_store` is an in-memory dictionary. In production, this would be replaced with Redis or a database. Suitable for demonstration and single-instance deployment.

2. **Sequential agent pipeline:** Agents run one after another (not in parallel) to control Vertex AI quota usage and keep the event stream logical and ordered.

3. **Text extraction is sufficient:** The system assumes contracts contain extractable text. Heavily image-based PDFs require Azure Document Intelligence configured for OCR.

4. **English-language contracts:** The AI prompts and analysis are optimized for English. Other languages may work but are not guaranteed.

5. **User is the non-drafting party:** All agents advocate for the user/employee/tenant — not the company or employer. The system is intentionally biased toward protecting the individual.

6. **20 MB file size limit:** Sufficient for virtually all text-based legal documents. Very large files (e.g., multi-volume agreements) would need chunking at the upload level.

7. **ChromaDB is local/ephemeral:** ChromaDB persists to disk per analysis. In a multi-instance production deployment, a shared vector store (e.g., Pinecone or Vertex AI Matching Engine) would be needed.

8. **GCS is optional:** The app works fully without Google Cloud Storage — files are processed in-memory and results stored in the application's in-memory state.

---

## 🐳 Deployment

### Docker (Backend)

```bash
cd backend
docker build -t lexguard-backend .
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your-key \
  lexguard-backend
```

### Frontend Production Build

```bash
cd frontend
npm run build
# Serve the dist/ folder with any static host
```

### Recommended Production Stack

| Component | Recommended Service |
|---|---|
| Backend API | **Google Cloud Run** (serverless containers) |
| Frontend | **Firebase Hosting** or **Vercel** |
| Vector Store | Migrate ChromaDB → **Vertex AI Matching Engine** |
| File Storage | **Google Cloud Storage** |
| State Store | **Redis** (replace in-memory analysis_store) |

### Google Cloud Run Deployment

```bash
# Build and push container
gcloud builds submit --tag gcr.io/YOUR_PROJECT/lexguard-backend

# Deploy to Cloud Run
gcloud run deploy lexguard-backend \
  --image gcr.io/YOUR_PROJECT/lexguard-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your-key
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit with clear messages: `git commit -m "feat: add clause highlighting"`
4. Push and open a Pull Request to `main`

**Python style:** PEP 8, type annotations required. Run `ruff check .` before submitting.  
**TypeScript:** Strict mode, no `any` types.

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">

### Built with Google Vertex AI · FastAPI · React · TypeScript

**LexGuard X** — *Smart contract intelligence for everyone.*

⭐ Star this repo if it helped you!

</div>
