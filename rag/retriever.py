"""
FAISS-based review retriever. Loads the pre-built index and handles similarity search.
"""

import os
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_INDEX_DIR = os.path.join(BASE_DIR, "data", "faiss_index")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class ReviewRetriever:
    """Loads FAISS index and searches for reviews similar to a query."""

    def __init__(self, index_dir: str = DEFAULT_INDEX_DIR):
        index_path = os.path.join(index_dir, "index.faiss")
        metadata_path = os.path.join(index_dir, "index_metadata.pkl")

        if not os.path.exists(index_path):
            raise FileNotFoundError(
                f"FAISS index not found at {index_path}. Run `python -m rag.build_index` first."
            )

        self.index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

        self.model = SentenceTransformer(MODEL_NAME)

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """
        Search for reviews most similar to the query.

        Returns list of dicts with review fields + 'score'.
        """
        query_embedding = self.model.encode(
            [query], normalize_embeddings=True
        ).astype(np.float32)

        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx == -1:
                continue
            review = dict(self.metadata[idx])
            review["score"] = float(score)
            results.append(review)

        return results


if __name__ == "__main__":
    retriever = ReviewRetriever()
    test_queries = [
        "best moisturizer for dry skin",
        "terrible product broke after one use",
        "great value for money hair products",
    ]
    for q in test_queries:
        print(f"\n🔍 Query: '{q}'")
        print("-" * 60)
        results = retriever.search(q, top_k=3)
        for i, r in enumerate(results):
            print(f"  #{i+1} (score={r['score']:.3f}) ⭐{r['rating']} | {r['title']}")
            print(f"     {r['text'][:100]}...")
