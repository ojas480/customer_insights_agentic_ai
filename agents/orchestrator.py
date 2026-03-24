"""
Agent Orchestrator — Coordinates the 3-agent pipeline:
  1. Retriever Agent → finds relevant reviews
  2. Analyzer Agent → extracts sentiment, pros/cons, themes
  3. Summarizer Agent → generates conversational response
"""

import time
from agents.retriever_agent import RetrieverAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.summarizer_agent import SummarizerAgent


class AgentOrchestrator:
    """Coordinates the sequential 3-agent pipeline."""

    def __init__(self):
        print("🔧 Initializing agents...")
        self.retriever = RetrieverAgent()
        self.analyzer = AnalyzerAgent()
        self.summarizer = SummarizerAgent()
        print("✅ All agents ready\n")

    def run(self, query: str, top_k: int = 10) -> dict:
        """
        Run the full agent pipeline for a user query.

        Returns:
            dict with 'response', 'analysis', 'reviews', 'query',
                  'rewritten_query', and 'timings'
        """
        timings = {}

        # Agent 1: Retrieve relevant reviews
        start = time.time()
        retrieval_result = self.retriever.run(query, top_k=top_k)
        timings["retriever"] = round(time.time() - start, 2)

        reviews = retrieval_result["reviews"]
        if not reviews:
            return {
                "response": "I couldn't find any relevant reviews for your query. Try rephrasing or asking about a different product.",
                "analysis": {},
                "reviews": [],
                "query": query,
                "rewritten_query": retrieval_result.get("rewritten_query", query),
                "timings": timings,
            }

        # Agent 2: Analyze the reviews
        start = time.time()
        analysis = self.analyzer.run(query, reviews)
        timings["analyzer"] = round(time.time() - start, 2)

        # Agent 3: Summarize into conversational response
        start = time.time()
        response = self.summarizer.run(query, analysis, reviews)
        timings["summarizer"] = round(time.time() - start, 2)

        timings["total"] = round(sum(timings.values()), 2)

        return {
            "response": response,
            "analysis": analysis,
            "reviews": reviews,
            "query": query,
            "rewritten_query": retrieval_result.get("rewritten_query", query),
            "timings": timings,
        }


if __name__ == "__main__":
    orch = AgentOrchestrator()
    result = orch.run("What are the best products for hair care?")

    print(f"Query: {result['query']}")
    print(f"Rewritten: {result['rewritten_query']}")
    print(f"\n{'='*60}")
    print(f"📝 Response:\n{result['response']}")
    print(f"\n{'='*60}")
    print(f"📊 Analysis: {result['analysis']}")
    print(f"\n⏱️  Timings: {result['timings']}")
    print(f"\n📄 Reviews returned: {len(result['reviews'])}")
