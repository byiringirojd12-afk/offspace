from typing import Dict, List

from .embedder import EmbeddingGenerator
from .loader import DocumentLoader
from .vectorstore import VectorStore


class KnowledgeManager:
    def __init__(self, source_dir: str = "."):
        self.loader = DocumentLoader(source_dir=source_dir)
        self.embedder = EmbeddingGenerator()
        self.vector_store = VectorStore(storage_dir=".offspace")

    def ingest_documents(self) -> None:
        documents = self.loader.load_documents()
        embeddings = self.embedder.embed(documents)
        for document, embedding in zip(documents, embeddings):
            self.vector_store.add(document, {"embedding": embedding})

    def retrieve(self, query: str) -> List[Dict[str, str]]:
        results = self.vector_store.search(query)
        return [{"text": item["text"], "metadata": item["metadata"]} for item in results]
