"""
Build a FAISS index from Amazon reviews using MiniLM sentence-transformer embeddings.
Reads data/amazon_reviews.csv, encodes review text, stores index + metadata.
"""

import os
import pickle
import time
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "amazon_reviews.csv")
INDEX_DIR = os.path.join(BASE_DIR, "data", "faiss_index")
INDEX_PATH = os.path.join(INDEX_DIR, "index.faiss")
METADATA_PATH = os.path.join(INDEX_DIR, "index_metadata.pkl")

# Model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 256


def build_index():
    """Load reviews, encode with MiniLM, build FAISS index."""
    print("📂 Loading reviews...")
    df = pd.read_csv(CSV_PATH)
    print(f"   Loaded {len(df):,} reviews\n")

    # Create searchable text: title + review body
    df["title"] = df["title"].fillna("")
    df["text"] = df["text"].fillna("")
    texts = (df["title"] + ". " + df["text"]).tolist()

    # Encode with MiniLM
    print(f"🧠 Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    print(f"   Embedding dimension: {model.get_sentence_embedding_dimension()}\n")

    print(f"⚡ Encoding {len(texts):,} reviews (batch_size={BATCH_SIZE})...")
    start = time.time()
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,  # for cosine similarity via inner product
    )
    elapsed = time.time() - start
    print(f"   Done in {elapsed:.1f}s ({len(texts)/elapsed:.0f} reviews/sec)\n")

    # Build FAISS index (Inner Product on normalized vectors = cosine similarity)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings.astype(np.float32))
    print(f"📦 FAISS index built: {index.ntotal:,} vectors, {dim} dimensions")

    # Save index
    os.makedirs(INDEX_DIR, exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    print(f"   Saved index → {INDEX_PATH}")

    # Save metadata (review data for each index position)
    metadata = df[["rating", "title", "text", "asin", "parent_asin",
                    "helpful_vote", "verified_purchase"]].to_dict("records")
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)
    print(f"   Saved metadata → {METADATA_PATH}")

    # Quick sanity check
    print(f"\n🔍 Sanity check — searching for 'moisturizer for dry skin'...")
    query_emb = model.encode(["moisturizer for dry skin"], normalize_embeddings=True)
    scores, indices = index.search(query_emb.astype(np.float32), 3)
    for rank, (idx, score) in enumerate(zip(indices[0], scores[0])):
        rev = metadata[idx]
        print(f"   #{rank+1} (score={score:.3f}) ⭐{rev['rating']} | {rev['title']}")
        print(f"      {rev['text'][:120]}...\n")

    print("✅ Index build complete!")


if __name__ == "__main__":
    build_index()
