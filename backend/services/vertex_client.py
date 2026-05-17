import os
import json
from dotenv import load_dotenv

load_dotenv()

# asia-south1 has limited Gemini model support.
# These regions support gemini-3.1-flash-lite:
SUPPORTED_REGIONS = ["us-central1", "us-east4", "europe-west4", "asia-northeast1"]


class VertexClient:
    """
    Google Cloud Vertex AI Gemini client.
    Priority:
      1. Vertex AI (GCP credits) — uses project: connect-7sp
      2. Gemini API key (GEMINI_API_KEY) — easiest fallback
    """

    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "")
        self.location = os.getenv("GCP_LOCATION", "us-central1")
        self.model_name = os.getenv("VERTEX_MODEL", "gemini-3.1-flash-lite")
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./gcp-key.json")
        self._model = None
        self._use_vertex = False
        self._gemini_model_name: str = self.model_name

        # If user set asia-south1 which doesn't fully support Gemini 3.1 Flash Lite,
        # override to us-central1 automatically
        if self.location not in SUPPORTED_REGIONS:
            print(f"[Vertex AI] Region '{self.location}' may not support {self.model_name}. "
                  f"Overriding to us-central1.")
            self.location = "us-central1"

    def _initialize(self):
        """Lazy initialization — only runs on first generate() call."""
        if self._model is not None:
            return

        # ── Option 1: Vertex AI (GCP credits) ──────────────────────────
        creds_exist = os.path.exists(self.credentials_path)
        project_set = bool(self.project_id and self.project_id not in ("", "your-gcp-project-id"))

        if project_set and creds_exist:
            try:
                import vertexai
                from vertexai.generative_models import GenerativeModel

                vertexai.init(project=self.project_id, location=self.location)
                self._model = GenerativeModel(self.model_name)
                self._use_vertex = True
                print(f"[Vertex AI] ✓ Connected | Project: {self.project_id} | "
                      f"Region: {self.location} | Model: {self.model_name}")
                return
            except Exception as e:
                print(f"[Vertex AI] ✗ Failed: {e}")
                print("[Vertex AI] Falling back to Gemini API key...")

        # ── Option 2: Gemini API Key (google-genai) ────────────────────
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if gemini_key and gemini_key != "your-gemini-api-key-here":
            try:
                from google import genai
                client = genai.Client(api_key=gemini_key)
                self._model = client
                self._use_vertex = False
                self._gemini_model_name = self.model_name
                print("[Gemini API] ✓ Connected via google-genai")
                return
            except Exception as e:
                print(f"[Gemini API] ✗ Failed: {e}")

        raise RuntimeError(
            "\n\n❌ No AI model configured!\n"
            "Choose ONE of these options:\n\n"
            "Option A (Vertex AI - uses GCP credits):\n"
            "  1. Download gcp-key.json from GCP → IAM → Service Accounts\n"
            "  2. Place it at: backend/gcp-key.json\n"
            "  3. Ensure VERTEX_MODEL=gemini-3.1-flash-lite in backend/.env\n\n"
            "Option B (Gemini API - easiest):\n"
            "  1. Go to https://aistudio.google.com/app/apikey\n"
            "  2. Create an API key (FREE tier available)\n"
            "  3. Set GEMINI_API_KEY=your-key in backend/.env\n"
        )

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        """Generate text. Returns string response."""
        self._initialize()

        try:
            if self._use_vertex:
                from vertexai.generative_models import GenerationConfig
                response = self._model.generate_content(
                    prompt,
                    generation_config=GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=4096,
                    )
                )
                return response.text
            else:
                from google.genai import types as genai_types
                response = self._model.models.generate_content(
                    model=self._gemini_model_name,
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=4096,
                    )
                )
                return response.text

        except Exception as e:
            print(f"[AI] Generation error: {e}")
            raise

    def generate_json(self, prompt: str, temperature: float = 0.2) -> dict:
        """Generate and parse JSON response. Strips markdown fences if present."""
        raw = self.generate(
            prompt + "\n\nCRITICAL: Return ONLY raw valid JSON. No markdown. No ```json. No explanation.",
            temperature=temperature
        )

        clean = raw.strip()

        # Strip markdown code fences
        if clean.startswith("```"):
            lines = clean.split("\n")
            # Remove opening ``` line and closing ``` line
            start = 1
            end = len(lines)
            if lines[-1].strip() in ("```", ""):
                end = len(lines) - 1
            clean = "\n".join(lines[start:end]).strip()

        try:
            return json.loads(clean)
        except json.JSONDecodeError as e:
            print(f"[AI] JSON parse error: {e}")
            print(f"[AI] Raw response (first 500 chars):\n{raw[:500]}")
            # Last resort: extract first {...} block
            import re
            match = re.search(r'\{[\s\S]*\}', clean)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
            raise RuntimeError(f"AI returned invalid JSON: {e}\nResponse: {raw[:300]}")
