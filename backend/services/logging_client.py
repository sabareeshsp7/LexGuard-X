"""
Google Cloud Logging client.
Provides structured, severity-tagged audit logging for
all critical operations — analysis lifecycle, AI calls, errors.
"""

import os
import logging
import sys
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# ── Standard Python logger used as fallback ───────────────────────────────────
_std_logger = logging.getLogger("lexguard")
if not _std_logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )
    _std_logger.addHandler(_handler)
    _std_logger.setLevel(logging.INFO)


class CloudLogger:
    """
    Wrapper around Google Cloud Logging.

    - When GCP credentials are present → structured logs sent to Cloud Logging
    - Otherwise → logs to stdout via standard Python logging (no silent failures)

    All logs include:
      analysis_id (when available)
      service name
      severity level
    """

    SERVICE_NAME = "lexguard-x"

    def __init__(self, logger_name: str = "lexguard-x"):
        self.logger_name = logger_name
        self.project_id = os.getenv("GCP_PROJECT_ID", "")
        self.credentials_path = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS", "./gcp-key.json"
        )
        self._cloud_logger = None
        self.enabled = (
            bool(self.project_id)
            and os.path.exists(self.credentials_path)
        )
        if self.enabled:
            self._initialize_cloud_logger()

    def _initialize_cloud_logger(self) -> None:
        """Set up the Cloud Logging handler."""
        try:
            import google.cloud.logging  # type: ignore
            client = google.cloud.logging.Client(project=self.project_id)
            self._cloud_logger = client.logger(self.logger_name)
            _std_logger.info(
                "[CloudLogger] Cloud Logging enabled for project '%s'",
                self.project_id,
            )
        except Exception as exc:
            _std_logger.warning(
                "[CloudLogger] Could not initialize Cloud Logging: %s — "
                "falling back to stdout",
                exc,
            )
            self.enabled = False

    # ──────────────────────────────────────────────────────────────
    #  Public logging methods
    # ──────────────────────────────────────────────────────────────

    def info(self, message: str, analysis_id: Optional[str] = None,
             **extra) -> None:
        """Log an informational event."""
        self._log("INFO", message, analysis_id, **extra)

    def warning(self, message: str, analysis_id: Optional[str] = None,
                 **extra) -> None:
        """Log a warning event."""
        self._log("WARNING", message, analysis_id, **extra)

    def error(self, message: str, analysis_id: Optional[str] = None,
              **extra) -> None:
        """Log an error event."""
        self._log("ERROR", message, analysis_id, **extra)

    def critical(self, message: str, analysis_id: Optional[str] = None,
                 **extra) -> None:
        """Log a critical event."""
        self._log("CRITICAL", message, analysis_id, **extra)

    # ──────────────────────────────────────────────────────────────
    #  Audit helpers
    # ──────────────────────────────────────────────────────────────

    def log_upload(self, analysis_id: str, filename: str,
                   file_size_bytes: int) -> None:
        """Audit log: file uploaded for analysis."""
        self.info(
            f"Contract uploaded: '{filename}' ({file_size_bytes:,} bytes)",
            analysis_id=analysis_id,
            event="upload",
            filename=filename,
            file_size_bytes=file_size_bytes,
        )

    def log_analysis_complete(self, analysis_id: str, risk_score: float,
                               findings_count: int, duration_s: float) -> None:
        """Audit log: analysis pipeline completed."""
        self.info(
            f"Analysis complete — risk={risk_score}/100, "
            f"findings={findings_count}, duration={duration_s}s",
            analysis_id=analysis_id,
            event="analysis_complete",
            risk_score=risk_score,
            findings_count=findings_count,
            duration_seconds=duration_s,
        )

    def log_analysis_error(self, analysis_id: str, error: str) -> None:
        """Audit log: analysis pipeline failed."""
        self.error(
            f"Analysis failed: {error}",
            analysis_id=analysis_id,
            event="analysis_error",
            error=error,
        )

    # ──────────────────────────────────────────────────────────────
    #  Internal
    # ──────────────────────────────────────────────────────────────

    def _log(self, severity: str, message: str,
             analysis_id: Optional[str], **extra) -> None:
        payload = {
            "message": message,
            "service": self.SERVICE_NAME,
            **extra,
        }
        if analysis_id:
            payload["analysis_id"] = analysis_id

        # Send to Cloud Logging
        if self.enabled and self._cloud_logger:
            try:
                self._cloud_logger.log_struct(
                    payload, severity=severity
                )
            except Exception as exc:
                _std_logger.warning("[CloudLogger] Cloud write failed: %s", exc)

        # Always mirror to stdout
        level = getattr(logging, severity, logging.INFO)
        _std_logger.log(level, "[%s] %s", analysis_id or "—", message)


# ── Module-level singleton for convenience import ─────────────────────────────
cloud_logger = CloudLogger()
