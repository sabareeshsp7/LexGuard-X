# LexGuard X — Complete Build Guide
### AI Rights & Contract Intelligence War Room
> **"Before you sign, AI argues for your rights."**

---

## Feasibility Assessment

Your proposed idea is **highly feasible** and extremely well-aligned with the problem statement. The multi-agent architecture gives you a clear edge over teams doing simple summarization. Below is the refined, competition-winning version.

---

## Final Refined Architecture

```
User Upload (PDF / DOCX / Scanned Image)
         |
         v
+------------------------------------------+
|  INGESTION LAYER                         |
|  Azure Document Intelligence (OCR/Parse) |
|  Azure AI Vision (Scanned Images)        |
+------------------+-----------------------+
                   | Raw Text
                   v
+------------------------------------------+
|  RAG LAYER (Google Cloud)                |
|  Text Chunking + Sentence Embeddings     |
|  ChromaDB (Vector Store)                 |
|  GCP Cloud Storage (PDF Archive)         |
+------------------+-----------------------+
                   | Relevant Chunks
                   v
+------------------------------------------+
|  MULTI-AGENT ORCHESTRATION (CrewAI)      |
|  Powered by: Vertex AI Gemini 1.5 Pro    |
|                                          |
|  Agent 1: Contract Classifier            |
|  Agent 2: Legal Risk Analyst             |
|  Agent 3: Privacy & Data Agent           |
|  Agent 4: Financial Liability Agent      |
|  Agent 5: Ambiguity Detector             |
|  Agent 6: Future Consequence Simulator   |
|  Agent 7: Negotiation Advisor            |
|  Agent 8: Judge / Synthesizer Agent      |
+------------------+-----------------------+
                   | Structured Risk Report
                   v
+------------------------------------------+
|  RISK ENGINE                             |
|  Severity Scoring (0-100)                |
|  Clause Classification                   |
|  Risk Category Mapping                   |
+------------------+-----------------------+
                   |
                   v
+------------------------------------------+
|  OUTPUT LAYER                            |
|  GCP Text-to-Speech (Voice Alerts)       |
|  Azure Speech (Narration)                |
|  FastAPI REST API                        |
+------------------+-----------------------+
                   |
                   v
+------------------------------------------+
|  FRONTEND (Vite + React + TypeScript)    |
|  Risk Dashboard                          |
|  Clause Viewer                           |
|  Agent Activity Feed (Live WebSocket)    |
|  Risk Radar Chart                        |
|  Negotiation Recommendations             |
|  Deployed: Firebase Hosting              |
+------------------------------------------+
```

---

## Prerequisites — What to Install

### System Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 20+ LTS | Frontend runtime |
| Git | Latest | Version control |
| VS Code | Latest | IDE |
| Google Cloud SDK | Latest | GCP access |
| Azure CLI | Latest | Azure access |

---

### Install Python 3.11+
```bash
# Windows — Download from:
# https://www.python.org/downloads/

# Verify:
python --version
```

### Install Node.js 20 LTS
```bash
# Download from: https://nodejs.org/

# Verify:
node --version
npm --version
```

### Install Google Cloud SDK
```bash
# Download from: https://cloud.google.com/sdk/docs/install

# After install, login:
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### Install Azure CLI
```bash
# Download from:
# https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

# Login:
az login
```

---

## Project Directory Structure

```
LexGuard X/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── agents/
│   │   ├── crew_orchestrator.py   # CrewAI setup
│   │   ├── legal_agents.py        # All 8 agents defined
│   │   └── agent_tools.py         # Custom agent tools
│   ├── services/
│   │   ├── document_parser.py     # Azure Doc Intelligence
│   │   ├── rag_engine.py          # ChromaDB + embeddings
│   │   ├── risk_engine.py         # Risk scoring logic
│   │   ├── vertex_client.py       # GCP Vertex AI client
│   │   └── storage_client.py      # GCP Cloud Storage
│   ├── models/
│   │   └── schemas.py             # Pydantic request/response models
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadZone.tsx
│   │   │   ├── AgentFeed.tsx
│   │   │   ├── RiskDashboard.tsx
│   │   │   ├── ClauseViewer.tsx
│   │   │   ├── RiskRadar.tsx
│   │   │   └── NegotiationPanel.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   └── Analysis.tsx
│   │   ├── api/
│   │   │   └── lexguard.ts
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## Step-by-Step Setup

### STEP 1: Initialize Workspace

```bash
cd "c:\LexGuard X"
```

---

### STEP 2: Backend Setup

```bash
cd "c:\LexGuard X"
mkdir backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

#### Install ALL Backend Dependencies

```bash
# Core API
pip install fastapi==0.111.0
pip install uvicorn[standard]==0.30.1
pip install python-multipart==0.0.9
pip install pydantic==2.7.1

# Document Parsing
pip install azure-ai-documentintelligence==1.0.0b3
pip install azure-cognitiveservices-vision-computervision==0.9.0
pip install pypdf==4.2.0
pip install python-docx==1.1.2
pip install pillow==10.3.0

# AI / LLM
pip install crewai==0.30.11
pip install crewai-tools==0.4.6
pip install google-cloud-aiplatform==1.56.0
pip install google-generativeai==0.7.2
pip install langchain==0.2.3
pip install langchain-google-vertexai==1.0.5

# RAG / Vector DB
pip install chromadb==0.5.3
pip install sentence-transformers==3.0.1

# GCP Services
pip install google-cloud-storage==2.17.0
pip install google-cloud-texttospeech==2.16.3

# Azure Speech
pip install azure-cognitiveservices-speech==1.39.0

# Utilities
pip install python-dotenv==1.0.1
pip install httpx==0.27.0
pip install websockets==12.0

# Save requirements
pip freeze > requirements.txt
```

---

### STEP 3: Frontend Setup

```bash
cd "c:\LexGuard X"

# Create Vite React TypeScript app
npm create vite@latest frontend -- --template react-ts
cd frontend

# Install dependencies
npm install

# Install project packages
npm install axios recharts framer-motion lucide-react react-dropzone
npm install @radix-ui/react-progress @radix-ui/react-tabs
npm install react-pdf pdfjs-dist

# Dev dependency
npm install -D @types/node
```

---

### STEP 4: GCP Setup

#### 4.1 Enable Required APIs
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable texttospeech.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable firebase.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

#### 4.2 Create Cloud Storage Buckets
```bash
gsutil mb -l us-central1 gs://lexguard-contracts-bucket
gsutil mb -l us-central1 gs://lexguard-reports-bucket
```

#### 4.3 Enable Vertex AI Gemini
```bash
# In Google Cloud Console:
# Vertex AI -> Model Garden -> Gemini 1.5 Pro -> Enable

gcloud config set project YOUR_GCP_PROJECT_ID
```

#### 4.4 Create Service Account + Download Key
```bash
gcloud iam service-accounts create lexguard-sa \
  --display-name="LexGuard Service Account"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:lexguard-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:lexguard-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:lexguard-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/texttospeech.client"

# Download key (place in backend/)
gcloud iam service-accounts keys create gcp-key.json \
  --iam-account=lexguard-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

---

### STEP 5: Azure Setup

#### 5.1 Create Resource Group
```bash
az group create --name lexguard-rg --location eastus
```

#### 5.2 Create Azure Document Intelligence
```bash
az cognitiveservices account create \
  --name lexguard-doc-intelligence \
  --resource-group lexguard-rg \
  --kind FormRecognizer \
  --sku S0 \
  --location eastus

# Get Keys:
az cognitiveservices account keys list \
  --name lexguard-doc-intelligence \
  --resource-group lexguard-rg
```

#### 5.3 Create Azure Speech Service
```bash
az cognitiveservices account create \
  --name lexguard-speech \
  --resource-group lexguard-rg \
  --kind SpeechServices \
  --sku S0 \
  --location eastus
```

---

### STEP 6: Environment Variables

Create `backend/.env`:
```env
# GCP Configuration
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
GCS_CONTRACTS_BUCKET=lexguard-contracts-bucket
GCS_REPORTS_BUCKET=lexguard-reports-bucket

# Vertex AI
VERTEX_MODEL=gemini-1.5-pro-001

# Azure Document Intelligence
AZURE_DOC_ENDPOINT=https://YOUR-RESOURCE.cognitiveservices.azure.com/
AZURE_DOC_KEY=your-azure-doc-intelligence-key

# Azure Speech
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=eastus

# App Config
CHROMA_PERSIST_DIR=./chroma_db
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

---

## Agent Architecture — The 8 Agents

| Agent | Role | Output |
|-------|------|--------|
| **Contract Classifier** | Detects contract type (employment/rental/privacy/SaaS) | contract_type string |
| **Legal Risk Analyst** | Finds harmful, exploitative, one-sided clauses | list of risk findings |
| **Privacy & Data Agent** | GDPR/data collection risk, third-party sharing | privacy_risks list |
| **Financial Liability Agent** | Hidden fees, auto-renewals, penalties | financial_risks list |
| **Ambiguity Detector** | Vague, contradictory, undefined language | ambiguity_flags list |
| **Future Consequence Simulator** | "What happens after you sign?" 3 scenarios | scenario objects |
| **Negotiation Advisor** | Suggests counter-clauses, alternative wording | negotiation_points list |
| **Judge / Synthesizer** | Combines all agent findings into final report | final_report object |

### Agent Debate Flow
```
Round 1: Contract Classifier runs first (sets context for all)
Round 2: Legal, Privacy, Financial, Ambiguity agents run in parallel
Round 3: Future Consequence agent runs with findings as input
Round 4: Negotiation Advisor proposes fixes
Round 5: Judge synthesizes everything into final scored report
```

---

## Prompt Engineering Strategy

### Legal Risk Agent — Master Prompt
```
You are a senior contract attorney with 20+ years of litigation experience.
You are EXCLUSIVELY representing the USER (not the company/employer).

Your task:
1. Identify if this clause is harmful, exploitative, or one-sided
2. Rate severity: CRITICAL / HIGH / MEDIUM / LOW
3. Explain in plain English what this means for the user (max 3 sentences)
4. Quote the exact problematic language from the clause
5. State what is INDUSTRY STANDARD for this type of clause
6. List the specific USER RIGHTS that are impacted

Contract Type: {contract_type}
Clause Text: {clause_text}

Return valid JSON only:
{
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "category": "NON_COMPETE|IP_TRANSFER|TERMINATION|ARBITRATION|PRIVACY|FINANCIAL|LIABILITY|OTHER",
  "plain_explanation": "...",
  "problematic_language": "exact quote",
  "industry_standard": "...",
  "user_rights_impacted": ["right1", "right2"],
  "user_impact_score": 0-10
}
```

### Future Consequence Simulator — Prompt
```
You are a legal scenario simulation expert and risk analyst.
Simulate 3 realistic future scenarios for this contract clause.

Scenario 1 (Best Case): Clause is signed but never enforced
Scenario 2 (Realistic): Clause is invoked in a typical dispute
Scenario 3 (Worst Case): Clause is maximally weaponized against user

For each scenario provide:
- trigger: what causes enforcement
- user_loss: what the user loses (financial, legal, personal)
- financial_impact: estimated dollar range
- probability: Low/Medium/High
- timeline: when this typically happens

Contract Type: {contract_type}
Clause: {clause_text}
Severity: {severity}

Return valid JSON only with "scenarios" array.
```

### Negotiation Advisor — Prompt
```
You are an expert contract negotiation specialist.
The user has identified a problematic clause. Suggest 3 negotiation alternatives.

For each alternative:
- revised_text: the new clause wording
- why_better: why this protects the user better
- likelihood_accepted: Low/Medium/High (will company accept this?)
- fallback: if company rejects, what minimum compromise to seek

Original Clause: {clause_text}
Issue Found: {risk_explanation}
Contract Type: {contract_type}

Return valid JSON only with "alternatives" array.
```

---

## Risk Scoring Formula

```python
def calculate_risk_score(findings: list) -> dict:
    weights = {
        "CRITICAL": 25,
        "HIGH": 15,
        "MEDIUM": 8,
        "LOW": 3
    }
    
    category_bonuses = {
        "IP_TRANSFER": 10,
        "NON_COMPETE": 8,
        "ARBITRATION": 7,
        "PRIVACY": 6,
    }
    
    base_score = sum(weights[f["severity"]] for f in findings)
    bonus = sum(
        category_bonuses.get(f["category"], 0) 
        for f in findings 
        if f["category"] in category_bonuses
    )
    
    risk_score = min(100, base_score + bonus)
    
    if risk_score >= 75:
        risk_level = "CRITICAL"
    elif risk_score >= 50:
        risk_level = "HIGH"
    elif risk_score >= 25:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    return {"score": risk_score, "level": risk_level}
```

---

## GCP Services Usage Map

| GCP Service | How Used in LexGuard X | Demo Impact |
|-------------|------------------------|-------------|
| **Vertex AI Gemini 1.5 Pro** | Powers ALL 8 agents | Critical |
| **Cloud Storage** | Stores uploaded contracts and reports | Medium |
| **Cloud Run** | Hosts FastAPI backend (live URL for demo) | High |
| **Firebase Hosting** | Hosts React frontend (live URL for demo) | High |
| **Text-to-Speech** | Voice narration of risk findings | High — wow factor |
| **Cloud Logging** | Logs agent execution for audit trail | Low |

## Azure Services Usage Map

| Azure Service | How Used in LexGuard X | Demo Impact |
|---------------|------------------------|-------------|
| **Document Intelligence** | OCR + structured PDF/DOCX extraction | Critical |
| **AI Vision** | Scanned document image analysis | High |
| **Speech Services** | Risk narration audio output | Medium |

---

## Running the Project Locally

### Start Backend
```bash
cd "c:\LexGuard X\backend"
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# API Docs: http://localhost:8000/docs
```

### Start Frontend
```bash
cd "c:\LexGuard X\frontend"
npm run dev
# Runs on http://localhost:5173
```

### API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Upload and analyze a contract |
| GET | `/api/analysis/{id}` | Get full analysis results |
| GET | `/api/analysis/{id}/report` | Download the risk PDF report |
| GET | `/api/health` | Health check |
| WebSocket | `/ws/analysis/{id}` | Live agent activity feed |

---

## Demo Sequence for Judges

```
1. Open browser → LexGuard X dashboard (Firebase-hosted URL)

2. Upload: employment_contract.pdf

3. Live agent feed appears (WebSocket):
   - Azure Document Intelligence extracting text...
   - RAG Engine chunking and embedding...
   - Contract Classifier: Type = Employment Agreement
   - Legal Risk Agent analyzing clauses...
   - Privacy Agent checking data policies...
   - Financial Agent scanning for penalties...
   - Future Agent simulating consequences...
   - Judge Agent synthesizing final verdict...

4. Dashboard renders automatically:
   - Risk Score: 82/100 — CRITICAL
   - 3 Critical findings in red
   - Radar chart: 6 risk categories visualized
   - Per-clause plain English explanations
   - 3-scenario future consequence simulation
   - Negotiation counter-proposals

5. GCP Text-to-Speech narrates:
   "Warning. Critical risk detected. Non-compete clause
    may prevent employment in this industry for 2 years.
    Broad IP transfer detected. All work created during
    and after employment belongs to the employer.
    Negotiation recommended before signing."
```

---

## Deployment

### Deploy Backend to Cloud Run

```bash
cd "c:\LexGuard X\backend"

# Create Dockerfile first (see below)

# Build and submit
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/lexguard-backend

# Deploy
gcloud run deploy lexguard-backend \
  --image gcr.io/YOUR_PROJECT_ID/lexguard-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300 \
  --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID
```

### Dockerfile for Backend
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Deploy Frontend to Firebase Hosting
```bash
cd "c:\LexGuard X\frontend"

# Update VITE_API_URL in .env to your Cloud Run URL
# VITE_API_URL=https://lexguard-backend-xxx-uc.a.run.app

npm run build

npm install -g firebase-tools
firebase login
firebase init hosting
# Public directory: dist
# Single-page app: Yes

firebase deploy
```

---

## Evaluation Criteria Coverage

| Evaluation Area | LexGuard X Solution | Rating |
|----------------|---------------------|--------|
| **Legal Reasoning Quality** | 8 specialized agents + Gemini 1.5 Pro chain-of-thought | 5/5 |
| **Risk Identification Accuracy** | RAG-grounded retrieval + multi-agent cross-validation | 5/5 |
| **Explainability** | Plain-English per clause + voice + visual dashboard | 5/5 |
| **Practical Applicability** | 6+ contract types, real upload, live analysis | 5/5 |
| **Technical Architecture** | Multi-cloud (GCP + Azure), RAG, CrewAI orchestration | 5/5 |
| **Adaptability** | Classifier agent auto-detects any contract type | 4/5 |
| **Innovation** | Agent debate + future scenario simulation + negotiation | 5/5 |
| **User Experience** | Live feed, risk radar chart, voice, responsive UI | 5/5 |

---

## Quick Wins for Judges

1. **Live WebSocket agent feed** — Judges see AI reasoning in real-time, not just a spinner
2. **Voice narration (GCP TTS)** — Instant wow factor, no other team will have this
3. **Future Consequence Simulation** — Completely unique feature not in any existing tool
4. **Negotiation Advisor output** — Actionable beyond just summarization
5. **Multi-cloud architecture slide** — Vertex AI + Azure + Firebase shows technical depth
6. **Risk radar chart** — Visual, instantly comprehensible across 6 categories
7. **Plain English clause explanations** — Directly solves the core problem statement

---

## API Keys Checklist

- [ ] GCP Project ID created and noted
- [ ] GCP Service Account JSON key downloaded to `backend/gcp-key.json`
- [ ] Vertex AI API enabled in GCP Console
- [ ] Cloud Storage buckets created
- [ ] Text-to-Speech API enabled
- [ ] Azure Document Intelligence endpoint + key copied
- [ ] Azure Speech key + region copied
- [ ] Firebase project created and initialized
- [ ] `.env` file filled out completely

---

## Sample Contracts for Demo Testing

| Contract Type | Key Risks to Demo |
|---------------|-------------------|
| Employment Agreement | Non-compete, broad IP transfer, at-will termination |
| Freelance Contract | IP ownership grab, payment delay clauses |
| Rental Agreement | Hidden fees, security deposit forfeit conditions |
| Privacy Policy | Excessive data collection, third-party data selling |
| SaaS Terms | Auto-renewal, unilateral price change, data ownership |
| Insurance Policy | Broad exclusion clauses, claim limitation periods |

> [!IMPORTANT]
> Use the **CUAD Dataset** (Contract Understanding Atticus Dataset) from https://www.atticusprojectai.org/cuad for testing. It contains 500+ real annotated contracts — perfect for demonstrating accuracy to judges.

> [!TIP]
> Build order: (1) Backend document parsing pipeline first, (2) Single agent working end-to-end, (3) Add all 8 agents, (4) Wire up frontend, (5) Add voice, (6) Deploy. This minimizes integration risk.

> [!WARNING]
> CrewAI with 8 agents on a full contract can take 3-5 minutes. Always show the live WebSocket agent feed so judges stay engaged during processing. Never let them stare at a blank loading screen.
