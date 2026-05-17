"""
Google Cloud Vision API client.
Provides OCR for scanned PDFs and image-based contracts.
Replaces Azure Document Intelligence for image parsing,
keeping the full stack on Google Cloud.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Guard: google-cloud-vision may not be installed
try:
    from google.cloud import vision as _vision_module  # type: ignore
    _VISION_AVAILABLE = True
except ImportError:
    _VISION_AVAILABLE = False
    _vision_module = None  # type: ignore
    logger.warning("[Vision] google-cloud-vision not installed — OCR via Vision disabled")


class VisionClient:
    """
    Google Cloud Vision API wrapper for document OCR.

    Supports:
      - JPEG, PNG, TIFF, BMP, GIF, WEBP, ICO, RAW, PDF (via async batch)
      - Falls back gracefully when credentials are absent.
    """

    def __init__(self):
        self.credentials_path = os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS", "./gcp-key.json"
        )
        self.project_id = os.getenv("GCP_PROJECT_ID", "")
        self._client = None
        # On Cloud Run, K_SERVICE is set — ADC handles auth automatically
        _is_cloud_run = bool(os.getenv("K_SERVICE"))
        self.enabled = (
            _VISION_AVAILABLE
            and bool(self.project_id)
            and (os.path.exists(self.credentials_path) or _is_cloud_run)
        )

    def _get_client(self):
        """Lazy-initialize the Vision client."""
        if self._client is None:
            self._client = _vision_module.ImageAnnotatorClient()
            logger.info("[Vision] Cloud Vision client initialized")
        return self._client

    def extract_text_from_image(self, image_bytes: bytes, filename: str) -> str:
        """
        Run DOCUMENT_TEXT_DETECTION on an image.

        Returns the full extracted text string, or raises RuntimeError
        if Vision is not configured or the request fails.
        """
        if not self.enabled:
            raise RuntimeError(
                "Google Cloud Vision is not configured. "
                "Set GCP_PROJECT_ID and ensure GOOGLE_APPLICATION_CREDENTIALS "
                "points to a valid service-account key."
            )

        try:
            client = self._get_client()
            image = _vision_module.Image(content=image_bytes)
            response = client.document_text_detection(image=image)

            if response.error.message:
                raise RuntimeError(f"Vision API error: {response.error.message}")

            full_text = response.full_text_annotation.text
            logger.info("[Vision] OCR extracted %d characters from '%s'",
                        len(full_text), filename)
            return full_text

        except Exception as exc:
            logger.error("[Vision] OCR failed for '%s': %s", filename, exc)
            raise

    def extract_text_from_pdf_page(self, page_bytes: bytes, filename: str) -> str:
        """
        Extract text from a single rendered PDF page (as PNG/JPEG bytes).
        Useful when individual pages are pre-rendered before passing to Vision.
        """
        return self.extract_text_from_image(page_bytes, filename)

    def is_available(self) -> bool:
        """Return True when Vision API credentials are present."""
        return self.enabled
