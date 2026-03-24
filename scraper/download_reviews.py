"""
Download Amazon Reviews from McAuley-Lab/Amazon-Reviews-2023 dataset.
Uses HuggingFace datasets library (v2.x) with trust_remote_code to load
the All_Beauty category via streaming, then saves first 15K reviews to CSV.
"""

import os
import time
import pandas as pd
from datasets import load_dataset

# Configuration
DATASET_NAME = "McAuley-Lab/Amazon-Reviews-2023"
CATEGORY = "raw_review_All_Beauty"
MAX_REVIEWS = 15000
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "amazon_reviews.csv")

COLUMNS = [
    "rating",
    "title",
    "text",
    "asin",
    "parent_asin",
    "user_id",
    "timestamp",
    "helpful_vote",
    "verified_purchase",
]


def download_reviews():
    """Stream reviews from HuggingFace and save to CSV."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"📦 Loading dataset: {DATASET_NAME} [{CATEGORY}]")
    print(f"🎯 Target: {MAX_REVIEWS:,} reviews")
    print()

    # Stream the dataset to avoid downloading everything
    dataset = load_dataset(
        DATASET_NAME,
        CATEGORY,
        split="full",
        streaming=True,
        trust_remote_code=True,
    )

    reviews = []
    start_time = time.time()

    for i, record in enumerate(dataset):
        if i >= MAX_REVIEWS:
            break

        review = {col: record.get(col, None) for col in COLUMNS}
        # Convert timestamp from ms to seconds for readability
        if review["timestamp"]:
            review["timestamp"] = int(review["timestamp"] / 1000)
        reviews.append(review)

        # Progress logging every 2000 reviews
        if (i + 1) % 2000 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            print(f"  ✅ {i + 1:,} reviews collected ({rate:.0f} reviews/sec)")

    elapsed = time.time() - start_time
    print(f"\n📊 Collected {len(reviews):,} reviews in {elapsed:.1f}s")

    # Save to CSV
    df = pd.DataFrame(reviews)

    # Drop reviews with empty text
    before = len(df)
    df = df.dropna(subset=["text"])
    df = df[df["text"].str.strip().astype(bool)]
    after = len(df)
    if before != after:
        print(f"🧹 Dropped {before - after} reviews with empty text ({after:,} remaining)")

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"💾 Saved to {OUTPUT_FILE}")

    # Summary
    print(f"\n{'='*50}")
    print(f"📈 SUMMARY")
    print(f"{'='*50}")
    print(f"   Rows:    {len(df):,}")
    print(f"   Columns: {list(df.columns)}")
    print(f"\n   Rating distribution:")
    for rating, count in df["rating"].value_counts().sort_index().items():
        stars = "⭐" * int(rating)
        print(f"     {stars} ({rating}): {count:,}")
    print(f"\n🔍 Sample review:")
    sample = df.iloc[0]
    print(f"   ⭐ {sample['rating']} | {sample['title']}")
    text_preview = str(sample['text'])[:200]
    print(f"   {text_preview}...")


if __name__ == "__main__":
    download_reviews()
