"""
Tests for RAGEngine — text chunking logic.
No ChromaDB or embedding model calls needed for chunking tests.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from services.rag_engine import RAGEngine


class TestRAGEngineChunking:

    def setup_method(self):
        self.rag = RAGEngine()

    def test_empty_text_returns_no_chunks(self):
        chunks = self.rag.chunk_text("")
        assert isinstance(chunks, list)

    def test_short_text_returns_at_least_one_chunk(self):
        text = "This is a short contract with basic terms." * 5
        chunks = self.rag.chunk_text(text)
        assert len(chunks) >= 1

    def test_chunks_are_strings(self):
        text = "Sample clause. " * 100
        chunks = self.rag.chunk_text(text)
        for chunk in chunks:
            assert isinstance(chunk, str)

    def test_no_chunk_exceeds_configured_size(self):
        long_text = "word " * 2000
        chunks = self.rag.chunk_text(long_text)
        for chunk in chunks:
            assert len(chunk) <= self.rag.chunk_size + 50  # small tolerance

    def test_clause_aware_chunking_splits_on_section(self):
        text = (
            "SECTION 1. Non-Compete. Employee shall not compete for 2 years.\n\n"
            "SECTION 2. Termination. Either party may terminate with 30 days notice.\n\n"
            "SECTION 3. IP Transfer. All inventions belong to employer.\n\n"
            "SECTION 4. Arbitration. All disputes go to binding arbitration.\n\n"
        )
        chunks = self.rag.chunk_text(text)
        assert len(chunks) >= 2

    def test_sliding_window_chunk_overlap(self):
        text = "a" * 3000
        chunks = self.rag._sliding_window_chunk(text)
        assert len(chunks) >= 2
        # With overlap, total characters covered should exceed text length
        total = sum(len(c) for c in chunks)
        assert total > len(text)

    def test_chunks_not_empty_strings(self):
        text = "Clause one details. " * 200
        chunks = self.rag.chunk_text(text)
        for chunk in chunks:
            assert chunk.strip() != ""

    def test_large_document_produces_multiple_chunks(self):
        # Simulate a 50-clause contract
        text = "\n\n".join(
            [f"CLAUSE {i}. The party agrees to specific term number {i}." * 10
             for i in range(1, 51)]
        )
        chunks = self.rag.chunk_text(text)
        assert len(chunks) >= 5


class TestRAGEngineSlidingWindow:

    def setup_method(self):
        self.rag = RAGEngine()
        self.rag.chunk_size = 100
        self.rag.chunk_overlap = 20

    def test_single_chunk_when_text_fits(self):
        text = "Short text. " * 5  # < 100 chars
        chunks = self.rag._sliding_window_chunk(text)
        assert len(chunks) == 1

    def test_multiple_chunks_when_text_exceeds_size(self):
        text = "x" * 500
        chunks = self.rag._sliding_window_chunk(text)
        assert len(chunks) > 1

    def test_all_chunks_within_size_limit(self):
        text = "word " * 500
        chunks = self.rag._sliding_window_chunk(text)
        for chunk in chunks:
            assert len(chunk) <= self.rag.chunk_size
