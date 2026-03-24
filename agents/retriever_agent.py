"""
Retriever Agent — Finds the most relevant reviews for a user query.
Uses FAISS-based ReviewRetriever, with optional LLM query rewriting.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from rag.retriever import ReviewRetriever

load_dotenv()


class RetrieverAgent:
    """Agent 1: Retrieves relevant reviews from FAISS index."""

    def __init__(self):
        self.retriever = ReviewRetriever()
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def _rewrite_query(self, query: str) -> str:
        """Use LLM to expand/rewrite query for better embedding search."""
        if not self.client:
            return query

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a search query optimizer. Rewrite the user's question "
                            "into a search query that would match relevant product reviews. "
                            "Keep it concise (under 30 words). Only return the rewritten query, "
                            "nothing else."
                        ),
                    },
                    {"role": "user", "content": query},
                ],
                temperature=0.3,
                max_tokens=60,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return query

    def run(self, query: str, top_k: int = 10) -> dict:
        """
        Retrieve relevant reviews for the query.

        Returns:
            dict with 'query', 'rewritten_query', and 'reviews' (list of dicts)
        """
        rewritten = self._rewrite_query(query)
        reviews = self.retriever.search(rewritten, top_k=top_k)

        return {
            "query": query,
            "rewritten_query": rewritten,
            "reviews": reviews,
        }
