"""
Analyzer Agent — Performs sentiment analysis, extracts pros/cons and themes
from a set of retrieved reviews using GPT-4o-mini.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a product review analyst. Given a user's question and a set of customer reviews, analyze them and return a JSON object with this exact structure:

{
  "sentiment": {
    "positive_pct": <number 0-100>,
    "negative_pct": <number 0-100>,
    "mixed_pct": <number 0-100>,
    "overall": "<positive|negative|mixed>"
  },
  "pros": ["<pro 1>", "<pro 2>", "<pro 3>"],
  "cons": ["<con 1>", "<con 2>", "<con 3>"],
  "themes": ["<theme 1>", "<theme 2>", "<theme 3>", "<theme 4>", "<theme 5>"],
  "rating_summary": {
    "average": <float>,
    "count": <int>,
    "distribution": {"1": <int>, "2": <int>, "3": <int>, "4": <int>, "5": <int>}
  }
}

Only return valid JSON, no explanations or markdown."""


class AnalyzerAgent:
    """Agent 2: Analyzes retrieved reviews for sentiment, patterns, pros/cons."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        ) if api_key else None

    def _format_reviews_for_prompt(self, reviews: list[dict]) -> str:
        """Format reviews into a readable string for the LLM."""
        lines = []
        for i, r in enumerate(reviews, 1):
            lines.append(
                f"Review {i}: ⭐{r['rating']} | \"{r['title']}\"\n"
                f"  {r['text'][:500]}\n"
                f"  Helpful votes: {r.get('helpful_vote', 0)} | "
                f"Verified: {r.get('verified_purchase', False)}"
            )
        return "\n\n".join(lines)

    def run(self, query: str, reviews: list[dict]) -> dict:
        """
        Analyze the retrieved reviews.

        Returns:
            dict with structured analysis (sentiment, pros, cons, themes, rating_summary)
        """
        reviews_text = self._format_reviews_for_prompt(reviews)

        if not self.client:
            # Fallback analysis without LLM
            ratings = [r["rating"] for r in reviews]
            return {
                "sentiment": {
                    "positive_pct": round(sum(1 for r in ratings if r >= 4) / max(len(ratings), 1) * 100),
                    "negative_pct": round(sum(1 for r in ratings if r <= 2) / max(len(ratings), 1) * 100),
                    "mixed_pct": round(sum(1 for r in ratings if r == 3) / max(len(ratings), 1) * 100),
                    "overall": "positive" if sum(ratings) / max(len(ratings), 1) >= 3.5 else "mixed",
                },
                "pros": ["See individual reviews"],
                "cons": ["See individual reviews"],
                "themes": ["product quality", "value", "effectiveness"],
                "rating_summary": {
                    "average": round(sum(ratings) / max(len(ratings), 1), 1),
                    "count": len(ratings),
                    "distribution": {str(i): ratings.count(float(i)) for i in range(1, 6)},
                },
            }

        try:
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"User question: {query}\n\n"
                            f"Reviews to analyze:\n\n{reviews_text}"
                        ),
                    },
                ],
                temperature=0.2,
                max_tokens=600,
                response_format={"type": "json_object"},
            )
            analysis = json.loads(response.choices[0].message.content)
        except Exception as e:
            # Fallback analysis if LLM fails
            ratings = [r["rating"] for r in reviews]
            analysis = {
                "sentiment": {
                    "positive_pct": round(sum(1 for r in ratings if r >= 4) / len(ratings) * 100),
                    "negative_pct": round(sum(1 for r in ratings if r <= 2) / len(ratings) * 100),
                    "mixed_pct": round(sum(1 for r in ratings if r == 3) / len(ratings) * 100),
                    "overall": "positive" if sum(ratings) / len(ratings) >= 3.5 else "mixed",
                },
                "pros": ["See reviews above"],
                "cons": ["See reviews above"],
                "themes": ["product quality"],
                "rating_summary": {
                    "average": round(sum(ratings) / len(ratings), 1),
                    "count": len(ratings),
                    "distribution": {str(i): ratings.count(float(i)) for i in range(1, 6)},
                },
                "error": str(e),
            }

        return analysis
