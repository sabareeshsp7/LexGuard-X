import os
import re
from dotenv import load_dotenv

load_dotenv()


class RAGEngine:
    """
    Retrieval-Augmented Generation engine.
    Chunks contract text, generates embeddings, stores in ChromaDB,
    and retrieves relevant chunks for agent analysis.
    """

    def __init__(self):
        self.chunk_size = int(os.getenv("MAX_CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        self.persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        self._client = None
        self._embedding_model = None

    def _get_client(self):
        if self._client is None:
            import chromadb
            self._client = chromadb.PersistentClient(path=self.persist_dir)
        return self._client

    def _get_embedding_model(self):
        if self._embedding_model is None:
            from sentence_transformers import SentenceTransformer
            self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("[RAG] Embedding model loaded: all-MiniLM-L6-v2")
        return self._embedding_model

    def chunk_text(self, text: str) -> list[str]:
        """
        Smart clause-aware chunking:
        - First splits on legal clause patterns (numbered sections, articles)
        - Then falls back to sentence-based chunking if needed
        """
        # Try to split on clause/section markers first
        clause_pattern = re.compile(
            r'(?=(?:SECTION|ARTICLE|CLAUSE|\d+\.|[A-Z]\.)[\s\S]{10,})',
            re.IGNORECASE
        )
        splits = clause_pattern.split(text)

        # Filter empty splits
        splits = [s.strip() for s in splits if len(s.strip()) > 50]

        if len(splits) < 3:
            # Fall back to sliding window chunking
            splits = self._sliding_window_chunk(text)

        # Ensure no chunk is too large
        final_chunks = []
        for chunk in splits:
            if len(chunk) <= self.chunk_size:
                final_chunks.append(chunk)
            else:
                sub_chunks = self._sliding_window_chunk(chunk)
                final_chunks.extend(sub_chunks)

        print(f"[RAG] Created {len(final_chunks)} chunks from {len(text)} characters")
        return final_chunks

    def _sliding_window_chunk(self, text: str) -> list[str]:
        """Sliding window chunking with overlap."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start += self.chunk_size - self.chunk_overlap
        return chunks

    def store_chunks(self, analysis_id: str, chunks: list[str]) -> str:
        """Store chunks with embeddings in ChromaDB. Returns collection name."""
        client = self._get_client()
        model = self._get_embedding_model()

        collection_name = f"lexguard_{analysis_id[:8]}"

        # Delete if exists (fresh analysis)
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass

        collection = client.create_collection(
            name=collection_name,
            metadata={"analysis_id": analysis_id}
        )

        # Generate embeddings in batches
        batch_size = 32
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            embeddings = model.encode(batch).tolist()
            ids = [f"chunk_{i + j}" for j in range(len(batch))]
            collection.add(
                documents=batch,
                embeddings=embeddings,
                ids=ids
            )

        print(f"[RAG] Stored {len(chunks)} chunks in collection '{collection_name}'")
        return collection_name

    def retrieve(self, analysis_id: str, query: str, n_results: int = 5) -> list[str]:
        """Retrieve most relevant chunks for a given query."""
        client = self._get_client()
        model = self._get_embedding_model()

        collection_name = f"lexguard_{analysis_id[:8]}"

        try:
            collection = client.get_collection(collection_name)
        except Exception:
            print(f"[RAG] Collection not found: {collection_name}")
            return []

        query_embedding = model.encode([query]).tolist()

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=min(n_results, collection.count())
        )

        documents = results.get("documents", [[]])[0]
        return documents

    def get_all_chunks(self, analysis_id: str) -> list[str]:
        """Get all stored chunks for an analysis."""
        client = self._get_client()
        collection_name = f"lexguard_{analysis_id[:8]}"

        try:
            collection = client.get_collection(collection_name)
            result = collection.get()
            return result.get("documents", [])
        except Exception:
            return []
