import math
import re
from typing import List


class EmbeddingService:
    """
    Lightweight, deterministic embedding & similarity service.
    Generates normalized 128-dimensional term-frequency vectors and handles hybrid scoring.
    """

    DIMENSION = 128

    @staticmethod
    def tokenize(text: str) -> List[str]:
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        return [token for token in cleaned.split() if len(token) > 1]

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        tokens = cls.tokenize(text)
        if not tokens:
            return [0.0] * cls.DIMENSION

        vector = [0.0] * cls.DIMENSION
        for token in tokens:
            # Hash token to dimension slot with sign
            h = hash(token)
            idx = abs(h) % cls.DIMENSION
            sign = 1.0 if (h % 2 == 0) else -1.0
            vector[idx] += sign

        # L2 Normalize
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [round(v / norm, 5) for v in vector]
        return vector

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        return max(0.0, min(1.0, dot))

    @classmethod
    def bm25_score(cls, query: str, document: str) -> float:
        query_tokens = set(cls.tokenize(query))
        doc_tokens = cls.tokenize(document)
        if not query_tokens or not doc_tokens:
            return 0.0

        matches = sum(1 for t in doc_tokens if t in query_tokens)
        return min(1.0, matches / (len(query_tokens) + 2))


embedding_service = EmbeddingService()
