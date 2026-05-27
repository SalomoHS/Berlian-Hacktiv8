from rank_bm25 import BM25Okapi
import numpy as np
from typing import List, Dict, Any

class BM25Service:
    def __init__(self):
        self.bm25 = None
        self.documents: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []

    def _extract_text(self, metadata: Dict[str, Any]) -> str:
        fields = [
            metadata.get("car_name", ""),
            metadata.get("spesifikasi_teknis", ""),
            metadata.get("fitur", ""),
            metadata.get("testimoni", ""),
        ]
        return " ".join(str(f) for f in fields if f)

    def _tokenize(self, text: str) -> List[str]:
        return text.lower().split()

    def build(self, matches: List[Dict[str, Any]]) -> None:
        self.documents = matches
        corpus_texts = [
            self._extract_text(m.get("metadata", {})) for m in matches
        ]
        self.tokenized_corpus = [self._tokenize(t) for t in corpus_texts]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def get_scores(self, query: str) -> np.ndarray:
        if self.bm25 is None:
            return np.zeros(len(self.documents))
        tokenized_query = self._tokenize(query)
        return self.bm25.get_scores(tokenized_query)
