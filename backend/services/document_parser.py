"""
Document parsing service.

Priority order for text extraction:
  1. Google Cloud Vision API  — best for images and scanned PDFs
  2. Azure Document Intelligence — premium structured layout parsing
  3. pypdf                     — fast local fallback for digital PDFs
  4. python-docx               — native DOCX parsing

All parsers log character counts and fall back gracefully.
"""

import os
import io
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class DocumentParser:
    """
    Multi-format contract text extractor.

    Supported formats:
      PDF  — Cloud Vision (if enabled) → pypdf fallback
      DOCX / DOC — python-docx
      PNG / JPG / JPEG / TIFF / BMP — Cloud Vision → Azure → RuntimeError
    """

    def __init__(self):
        # Azure Document Intelligence (optional)
        self.azure_endpoint = os.getenv("AZURE_DOC_ENDPOINT", "")
        self.azure_key = os.getenv("AZURE_DOC_KEY", "")
        self.use_azure = bool(
            self.azure_endpoint
            and self.azure_key
            and self.azure_endpoint
            != "https://YOUR-RESOURCE.cognitiveservices.azure.com/"
        )

        # Google Cloud Vision (preferred for images / scanned PDFs)
        from services.vision_client import VisionClient
        self._vision = VisionClient()

    # ──────────────────────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────────────────────

    def parse(self, file_bytes: bytes, filename: str) -> str:
        """
        Parse a document and return its full extracted text.

        Args:
            file_bytes: Raw file content.
            filename:   Original filename (used to detect extension).

        Returns:
            Extracted plain text string.

        Raises:
            ValueError:   Unsupported file extension.
            RuntimeError: Extraction failed on all providers.
        """
        if not filename:
            raise ValueError("filename must not be empty")
        if not file_bytes:
            raise ValueError("file_bytes must not be empty")

        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            return self._parse_pdf(file_bytes, filename)
        elif ext in {".docx", ".doc"}:
            return self._parse_docx(file_bytes)
        elif ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
            return self._parse_image(file_bytes, filename)
        else:
            raise ValueError(
                f"Unsupported file type '{ext}'. "
                "Allowed: .pdf .docx .doc .png .jpg .jpeg .tiff .bmp"
            )

    # ──────────────────────────────────────────────────────────────
    #  PDF
    # ──────────────────────────────────────────────────────────────

    def _parse_pdf(self, file_bytes: bytes, filename: str) -> str:
        """
        PDF extraction priority:
          1. Google Cloud Vision API (handles scanned / image-heavy PDFs)
          2. Azure Document Intelligence
          3. pypdf (digital PDFs only)
        """
        # Try pypdf first to check if it's a native digital PDF
        try:
            text = self._pypdf_parse(file_bytes)
            if len(text.strip()) >= 200:
                logger.info(
                    "[Parser] pypdf extracted %d chars from '%s'",
                    len(text), filename,
                )
                return text
            # Not enough text — likely a scanned PDF; fall through to OCR
            logger.info(
                "[Parser] pypdf yielded only %d chars — trying OCR", len(text)
            )
        except Exception as exc:
            logger.warning("[Parser] pypdf failed: %s — trying OCR", exc)

        # Try Google Cloud Vision OCR
        if self._vision.is_available():
            try:
                text = self._vision_ocr(file_bytes, filename)
                if text.strip():
                    return text
            except Exception as exc:
                logger.warning("[Parser] Cloud Vision failed: %s", exc)

        # Try Azure Document Intelligence
        if self.use_azure:
            try:
                return self._azure_parse(file_bytes, filename)
            except Exception as exc:
                logger.warning("[Parser] Azure failed: %s — using pypdf", exc)

        # Final fallback: return whatever pypdf got
        return self._pypdf_parse(file_bytes)

    # ──────────────────────────────────────────────────────────────
    #  Image
    # ──────────────────────────────────────────────────────────────

    def _parse_image(self, file_bytes: bytes, filename: str) -> str:
        """
        Image extraction priority:
          1. Google Cloud Vision API
          2. Azure Document Intelligence
        """
        if self._vision.is_available():
            try:
                text = self._vision_ocr(file_bytes, filename)
                if text.strip():
                    return text
            except Exception as exc:
                logger.warning("[Parser] Cloud Vision failed: %s", exc)

        if self.use_azure:
            return self._azure_parse(file_bytes, filename)

        raise RuntimeError(
            "Image OCR requires either Google Cloud Vision (GCP_PROJECT_ID + "
            "gcp-key.json) or Azure Document Intelligence credentials. "
            "Please configure at least one OCR provider."
        )

    # ──────────────────────────────────────────────────────────────
    #  Provider implementations
    # ──────────────────────────────────────────────────────────────

    def _vision_ocr(self, file_bytes: bytes, filename: str) -> str:
        """Delegate to Google Cloud Vision client."""
        text = self._vision.extract_text_from_image(file_bytes, filename)
        logger.info(
            "[Parser] Cloud Vision extracted %d chars from '%s'",
            len(text), filename,
        )
        return text

    def _azure_parse(self, file_bytes: bytes, filename: str) -> str:
        """Parse via Azure Document Intelligence prebuilt-read model."""
        try:
            from azure.ai.documentintelligence import DocumentIntelligenceClient  # type: ignore
            from azure.core.credentials import AzureKeyCredential  # type: ignore

            client = DocumentIntelligenceClient(
                endpoint=self.azure_endpoint,
                credential=AzureKeyCredential(self.azure_key),
            )
            poller = client.begin_analyze_document(
                "prebuilt-read",
                analyze_request=file_bytes,
                content_type="application/octet-stream",
            )
            result = poller.result()

            lines = []
            for page in result.pages:
                for line in page.lines:
                    lines.append(line.content)

            full_text = "\n".join(lines)
            logger.info(
                "[Parser] Azure extracted %d chars from '%s'",
                len(full_text), filename,
            )
            return full_text

        except Exception as exc:
            logger.error("[Parser] Azure parse error: %s", exc)
            raise RuntimeError(f"Azure parsing failed: {exc}") from exc

    def _pypdf_parse(self, file_bytes: bytes) -> str:
        """Parse digital PDF using pypdf."""
        try:
            from pypdf import PdfReader  # type: ignore

            reader = PdfReader(io.BytesIO(file_bytes))
            parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    parts.append(text)
            full_text = "\n\n".join(parts)
            logger.info(
                "[Parser] pypdf extracted %d chars from %d pages",
                len(full_text), len(reader.pages),
            )
            return full_text
        except Exception as exc:
            raise RuntimeError(f"pypdf parsing failed: {exc}") from exc

    def _parse_docx(self, file_bytes: bytes) -> str:
        """Parse DOCX/DOC using python-docx."""
        try:
            from docx import Document  # type: ignore

            doc = Document(io.BytesIO(file_bytes))
            paragraphs = [
                p.text for p in doc.paragraphs if p.text.strip()
            ]
            full_text = "\n\n".join(paragraphs)
            logger.info(
                "[Parser] DOCX extracted %d chars, %d paragraphs",
                len(full_text), len(paragraphs),
            )
            return full_text
        except Exception as exc:
            raise RuntimeError(f"DOCX parsing failed: {exc}") from exc
