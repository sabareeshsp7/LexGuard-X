"""
Google Cloud Firestore client.
Persists analysis history so users can retrieve past results
without re-uploading documents.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Guard: google-cloud-firestore may not be installed
try:
    from google.cloud import firestore as _firestore_module  # type: ignore
    _FIRESTORE_AVAILABLE = True
except ImportError:
    _FIRESTORE_AVAILABLE = False
    logger.warning("[Firestore] google-cloud-firestore not installed — history persistence disabled")

COLLECTION_ANALYSES = "analyses"


class FirestoreClient:
    """
    Cloud Firestore wrapper for analysis persistence.

    Schema (collection: analyses):
      analysis_id   : str  — document ID
      filename      : str
      contract_type : str
      risk_score    : float
      risk_level    : str
      findings_count: int
      status        : str  (processing | complete | error)
      created_at    : str  (ISO-8601 UTC)
      result        : dict — full AnalysisResult payload

    Gracefully no-ops when Firestore is not configured.
    """

    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "")
        self.credentials_path = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS", "./gcp-key.json"
        )
        self._db = None
        # On Cloud Run, K_SERVICE is set — ADC handles auth automatically
        _is_cloud_run = bool(os.getenv("K_SERVICE"))
        self.enabled = (
            _FIRESTORE_AVAILABLE
            and bool(self.project_id)
            and (os.path.exists(self.credentials_path) or _is_cloud_run)
        )

    def _get_db(self):
        """Lazy-initialize the Firestore client."""
        if self._db is None:
            self._db = _firestore_module.Client(project=self.project_id)
            logger.info("[Firestore] Client initialized for project '%s'",
                        self.project_id)
        return self._db

    # ──────────────────────────────────────────────────────────────
    #  Write operations
    # ──────────────────────────────────────────────────────────────

    def create_analysis_record(
        self, analysis_id: str, filename: str
    ) -> None:
        """Create an initial 'processing' record when upload starts."""
        if not self.enabled:
            return

        try:
            db = self._get_db()
            db.collection(COLLECTION_ANALYSES).document(analysis_id).set({
                "analysis_id": analysis_id,
                "filename": filename,
                "status": "processing",
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            logger.info("[Firestore] Created record for analysis '%s'",
                        analysis_id)
        except Exception as exc:
            logger.error("[Firestore] create_analysis_record failed: %s", exc)

    def save_analysis_result(
        self, analysis_id: str, result: dict, gcs_url: str = ""
    ) -> None:
        """Persist the completed analysis result to Firestore."""
        if not self.enabled:
            return

        try:
            db = self._get_db()
            # risk_score can be a dict, float, int, or string depending on pipeline version
            raw_risk = result.get("risk_score", {})
            if isinstance(raw_risk, dict):
                overall_score = raw_risk.get("overall_score", 0)
                risk_level   = raw_risk.get("level", "LOW")
            else:
                # Scalar value — treat as the score directly
                try:
                    overall_score = float(raw_risk)
                except (TypeError, ValueError):
                    overall_score = 0
                risk_level = "LOW"

            db.collection(COLLECTION_ANALYSES).document(analysis_id).set({
                "analysis_id": analysis_id,
                "filename": result.get("file_name", "") if isinstance(result, dict) else "",
                "contract_type": result.get("contract_type", "Unknown") if isinstance(result, dict) else "Unknown",
                "risk_score": overall_score,
                "risk_level": risk_level,
                "findings_count": len(result.get("findings", [])) if isinstance(result, dict) else 0,
                "status": "complete",
                "gcs_url": gcs_url,
                "created_at": result.get("created_at", datetime.now(timezone.utc).isoformat()) if isinstance(result, dict) else datetime.now(timezone.utc).isoformat(),
                "result": result,
            }, merge=True)
            logger.info("[Firestore] Saved completed result for '%s'", analysis_id)
        except Exception as exc:
            logger.error("[Firestore] save_analysis_result failed: %s", exc)

    def mark_analysis_error(self, analysis_id: str, error: str) -> None:
        """Mark an analysis record as failed."""
        if not self.enabled:
            return

        try:
            db = self._get_db()
            db.collection(COLLECTION_ANALYSES).document(analysis_id).set({
                "status": "error",
                "error": error,
            }, merge=True)
            logger.warning("[Firestore] Marked '%s' as error: %s",
                           analysis_id, error)
        except Exception as exc:
            logger.error("[Firestore] mark_analysis_error failed: %s", exc)

    # ──────────────────────────────────────────────────────────────
    #  Read operations
    # ──────────────────────────────────────────────────────────────

    def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        """Retrieve a single analysis record by ID."""
        if not self.enabled:
            return None

        try:
            db = self._get_db()
            doc = db.collection(COLLECTION_ANALYSES).document(analysis_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as exc:
            logger.error("[Firestore] get_analysis failed: %s", exc)
            return None

    def list_recent_analyses(self, limit: int = 20) -> List[Dict]:
        """Return the most recent analyses ordered by creation time."""
        if not self.enabled:
            return []

        try:
            db = self._get_db()
            docs = (
                db.collection(COLLECTION_ANALYSES)
                .order_by("created_at", direction="DESCENDING")
                .limit(limit)
                .stream()
            )
            return [
                {k: v for k, v in doc.to_dict().items() if k != "result"}
                for doc in docs
            ]
        except Exception as exc:
            logger.error("[Firestore] list_recent_analyses failed: %s", exc)
            return []

    def is_available(self) -> bool:
        """Return True when Firestore credentials are present."""
        return self.enabled
