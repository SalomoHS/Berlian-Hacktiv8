import numpy as np
from typing import List, Dict, Any

def reciprocal_rank_fusion(
    dense_scores: np.ndarray,
    sparse_scores: np.ndarray,
    dense_weight: float = 0.6,
    sparse_weight: float = 0.4,
    k: int = 60,
) -> np.ndarray:
    n = len(dense_scores)
    dense_ranks = np.argsort(np.argsort(-dense_scores)) + 1
    sparse_ranks = np.argsort(np.argsort(-sparse_scores)) + 1

    fused = (
        dense_weight  / (k + dense_ranks) +
        sparse_weight / (k + sparse_ranks)
    )
    return fused
