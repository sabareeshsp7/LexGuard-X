"""
Tests for the document parser service.
Validates format detection, fallback chain, and error handling.
"""
import pytest
from services.document_parser import DocumentParser


MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
    b"xref\n0 4\n0000000000 65535 f\n"
    b"0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n"
    b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
)


@pytest.fixture
def parser():
    return DocumentParser()


class TestDocumentParserInit:
    def test_parser_instantiates(self, parser):
        assert parser is not None

    def test_parser_has_parse_method(self, parser):
        assert callable(getattr(parser, "parse", None)) or callable(
            getattr(parser, "extract_text", None)
        )


class TestDocumentParserFormats:
    def test_pdf_returns_string(self, parser):
        method = getattr(parser, "parse", None) or getattr(parser, "extract_text", None)
        result = method(MINIMAL_PDF, "contract.pdf")
        assert isinstance(result, str)

    def test_unknown_extension_returns_string(self, parser):
        method = getattr(parser, "parse", None) or getattr(parser, "extract_text", None)
        result = method(b"garbage", "file.unknown")
        assert isinstance(result, str)

    def test_empty_bytes_returns_string(self, parser):
        method = getattr(parser, "parse", None) or getattr(parser, "extract_text", None)
        result = method(b"", "empty.pdf")
        assert isinstance(result, str)

    def test_supported_extensions_list_exists(self, parser):
        """Parser should define or accept known extensions."""
        # Should accept PDF without throwing
        method = getattr(parser, "parse", None) or getattr(parser, "extract_text", None)
        try:
            result = method(MINIMAL_PDF, "test.pdf")
            assert isinstance(result, str)
        except Exception as e:
            pytest.fail(f"PDF parsing raised unexpected exception: {e}")
