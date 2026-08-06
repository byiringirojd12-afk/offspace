from typing import List


class EmbeddingGenerator:
    def __init__(self):
        self.model_name = "local-embedding-sim"

    def embed(self, texts: List[str]) -> List[List[float]]:
        embeddings: List[List[float]] = []
        for text in texts:
            values = [float(len(text)) / 100.0]
            embeddings.append(values)
        return embeddings
