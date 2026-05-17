import os
import io
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class DocumentParser:
    """
    Handles document parsing using Azure Document Intelligence (for PDF/DOCX)
    with a fallback to pypdf for basic PDF parsing when Azure is not configured.
    """

    def __init__(self):
        self.azure_endpoint = os.getenv("AZURE_DOC_ENDPOINT", "")
        self.azure_key = os.getenv("AZURE_DOC_KEY", "")
        self.use_azure = bool(self.azure_endpoint and self.azure_key and
                              self.azure_endpoint != "https://YOUR-RESOURCE.cognitiveservices.azure.com/")

    def parse(self, file_bytes: bytes, filename: str) -> str:
        """Parse document and return extracted text."""
        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            return self._parse_pdf(file_bytes, filename)
        elif ext in [".docx", ".doc"]:
            return self._parse_docx(file_bytes)
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            return self._parse_image(file_bytes, filename)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _parse_pdf(self, file_bytes: bytes, filename: str) -> str:
        """Parse PDF using Azure Document Intelligence or pypdf fallback."""
        if self.use_azure:
            return self._azure_parse(file_bytes, filename)
        else:
            return self._pypdf_fallback(file_bytes)

    def _azure_parse(self, file_bytes: bytes, filename: str) -> str:
        """Use Azure Document Intelligence for robust parsing."""
        try:
            from azure.ai.documentintelligence import DocumentIntelligenceClient
            from azure.core.credentials import AzureKeyCredential

            client = DocumentIntelligenceClient(
                endpoint=self.azure_endpoint,
                credential=AzureKeyCredential(self.azure_key)
            )

            poller = client.begin_analyze_document(
                "prebuilt-read",
                analyze_request=file_bytes,
                content_type="application/octet-stream"
            )
            result = poller.result()

            extracted_text = []
            for page in result.pages:
                for line in page.lines:
                    extracted_text.append(line.content)

            full_text = "\n".join(extracted_text)
            print(f"[Azure Parser] Extracted {len(full_text)} characters from {filename}")
            return full_text

        except Exception as e:
            print(f"[Azure Parser] Error: {e}. Falling back to pypdf.")
            return self._pypdf_fallback(file_bytes)

    def _pypdf_fallback(self, file_bytes: bytes) -> str:
        """Fallback PDF parser using pypdf."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            full_text = "\n\n".join(text_parts)
            print(f"[pypdf] Extracted {len(full_text)} characters from {len(reader.pages)} pages")
            return full_text
        except Exception as e:
            raise RuntimeError(f"PDF parsing failed: {e}")

    def _parse_docx(self, file_bytes: bytes) -> str:
        """Parse DOCX using python-docx."""
        try:
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            full_text = "\n\n".join(paragraphs)
            print(f"[DOCX Parser] Extracted {len(full_text)} characters, {len(paragraphs)} paragraphs")
            return full_text
        except Exception as e:
            raise RuntimeError(f"DOCX parsing failed: {e}")

    def _parse_image(self, file_bytes: bytes, filename: str) -> str:
        """Parse scanned image using Azure Computer Vision via Document Intelligence."""
        if self.use_azure:
            return self._azure_parse(file_bytes, filename)
        else:
            raise RuntimeError(
                "Image parsing requires Azure Document Intelligence. "
                "Please configure AZURE_DOC_ENDPOINT and AZURE_DOC_KEY."
            )
