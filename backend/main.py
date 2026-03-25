"""
FastAPI backend for CustomerInsight.
Exposes API endpoints for querying the 3-agent pipeline.
"""

import os
import threading
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from agents.orchestrator import AgentOrchestrator
from backend.schemas import (
    QueryRequest,
    QueryResponse,
    AnalysisResult,
    SentimentResult,
    RatingSummary,
    ReviewResult,
    StatsResponse,
)

load_dotenv()

app = FastAPI(
    title="CustomerInsight API",
    description="3-Agent RAG pipeline for analyzing Amazon product reviews",
    version="1.0.0",
)

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        os.environ.get("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
orchestrator: AgentOrchestrator | None = None
dataset_stats: dict = {}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "amazon_reviews.csv")


def init_orchestrator():
    global orchestrator
    print("🔧 Initializing orchestrator in background...")
    orchestrator = AgentOrchestrator()
    print("✅ Orchestrator loaded!")

@app.on_event("startup")
def startup():
    """Load agents and compute dataset stats on startup."""
    global dataset_stats

    # Start orchestrator load in background so it doesn't block port binding
    threading.Thread(target=init_orchestrator, daemon=True).start()

    # Compute dataset stats (then free the dataframe)
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        rating_dist = df["rating"].value_counts().sort_index().to_dict()
        dataset_stats = {
            "total_reviews": len(df),
            "average_rating": round(df["rating"].mean(), 2),
            "category": "All Beauty",
            "rating_distribution": {str(int(k)): int(v) for k, v in rating_dist.items()},
        }
        del df  # free memory before loading agents


@app.get("/api/health")
def health():
    return {"status": "ok", "agents_loaded": orchestrator is not None}


@app.get("/api/stats", response_model=StatsResponse)
def stats():
    if not dataset_stats:
        raise HTTPException(status_code=503, detail="Stats not loaded")
    return dataset_stats


@app.post("/api/query", response_model=QueryResponse)
def query(req: QueryRequest):
    """Run the 3-agent pipeline for a user query."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Agents not initialized")

    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    result = orchestrator.run(req.query, top_k=req.top_k)

    # Parse analysis into structured format
    raw_analysis = result.get("analysis", {})
    sentiment_data = raw_analysis.get("sentiment", {})
    rating_data = raw_analysis.get("rating_summary", {})

    analysis = AnalysisResult(
        sentiment=SentimentResult(**sentiment_data) if sentiment_data else SentimentResult(),
        pros=raw_analysis.get("pros", []),
        cons=raw_analysis.get("cons", []),
        themes=raw_analysis.get("themes", []),
        rating_summary=RatingSummary(**rating_data) if rating_data else RatingSummary(),
    )

    reviews = [
        ReviewResult(
            rating=r.get("rating", 0),
            title=r.get("title"),
            text=r.get("text"),
            asin=r.get("asin"),
            helpful_vote=r.get("helpful_vote"),
            verified_purchase=r.get("verified_purchase"),
            score=r.get("score", 0),
        )
        for r in result.get("reviews", [])
    ]

    return QueryResponse(
        response=result.get("response", ""),
        analysis=analysis,
        reviews=reviews,
        query=result.get("query", req.query),
        rewritten_query=result.get("rewritten_query", ""),
        timings=result.get("timings", {}),
    )
