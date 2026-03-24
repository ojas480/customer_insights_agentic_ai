"""
Summarizer Agent — Synthesizes a conversational, helpful response
from the analysis and reviews, citing specific reviews when relevant.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a helpful product insight assistant called CustomerInsight. Using the analysis and customer reviews provided, give the user a conversational, helpful answer to their question.

Guidelines:
- Be concise but thorough (2-4 paragraphs max)
- Cite specific reviews when relevant (e.g., "One verified buyer noted...")
- Mention the sentiment breakdown naturally
- Highlight key pros and cons
- If the data is limited, acknowledge it
- Use a friendly, professional tone
- Don't use markdown headers, just flowing paragraphs"""


class SummarizerAgent:
    """Agent 3: Synthesizes final conversational response from analysis + reviews."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        ) if api_key else None

    def _format_context(self, query: str, analysis: dict, reviews: list[dict]) -> str:
        """Build context string for the LLM."""
        # Format analysis
        sentiment = analysis.get("sentiment", {})
        pros = analysis.get("pros", [])
        cons = analysis.get("cons", [])
        themes = analysis.get("themes", [])
        rating = analysis.get("rating_summary", {})

        context = f"""User Question: {query}

Analysis Summary:
- Overall sentiment: {sentiment.get('overall', 'unknown')} ({sentiment.get('positive_pct', 0)}% positive, {sentiment.get('negative_pct', 0)}% negative)
- Average rating: {rating.get('average', 'N/A')}/5 across {rating.get('count', 0)} relevant reviews
- Top pros: {', '.join(pros)}
- Top cons: {', '.join(cons)}
- Key themes: {', '.join(themes)}

Relevant Reviews:
"""
        for i, r in enumerate(reviews[:5], 1):
            verified = "✓ Verified" if r.get("verified_purchase") else ""
            context += (
                f"\n[Review {i}] ⭐{r['rating']} {verified}\n"
                f"  Title: {r['title']}\n"
                f"  \"{r['text'][:300]}\"\n"
            )

        return context

    def run(self, query: str, analysis: dict, reviews: list[dict]) -> str:
        """
        Generate a conversational summary response.

        Returns:
            str — the final response text
        """
        context = self._format_context(query, analysis, reviews)

        if not self.client:
            # Fallback summary without LLM
            sentiment = analysis.get("sentiment", {})
            pros = analysis.get("pros", [])
            cons = analysis.get("cons", [])
            avg = analysis.get("rating_summary", {}).get("average", "N/A")
            return (
                f"Based on {len(reviews)} relevant reviews (avg rating: {avg}/5), "
                f"the overall sentiment is {sentiment.get('overall', 'mixed')} "
                f"({sentiment.get('positive_pct', 0)}% positive). "
                f"Key pros: {', '.join(pros[:3])}. "
                f"Key cons: {', '.join(cons[:3])}. "
                f"Set GEMINI_API_KEY in .env for more detailed AI-generated summaries."
            )

        try:
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": context},
                ],
                temperature=0.7,
                max_tokens=800,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return (
                f"I found {len(reviews)} relevant reviews for your question. "
                f"The overall sentiment is {analysis.get('sentiment', {}).get('overall', 'mixed')}. "
                f"Unfortunately, I couldn't generate a detailed summary right now. "
                f"Error: {str(e)}"
            )
