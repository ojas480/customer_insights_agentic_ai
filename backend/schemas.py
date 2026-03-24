"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    top_k: int = 10


class ReviewResult(BaseModel):
    rating: float
    title: str | None
    text: str | None
    asin: str | None
    helpful_vote: int | None
    verified_purchase: bool | None
    score: float


class SentimentResult(BaseModel):
    positive_pct: float = 0
    negative_pct: float = 0
    mixed_pct: float = 0
    overall: str = "unknown"


class RatingSummary(BaseModel):
    average: float = 0
    count: int = 0
    distribution: dict = {}


class AnalysisResult(BaseModel):
    sentiment: SentimentResult = SentimentResult()
    pros: list[str] = []
    cons: list[str] = []
    themes: list[str] = []
    rating_summary: RatingSummary = RatingSummary()


class QueryResponse(BaseModel):
    response: str
    analysis: AnalysisResult
    reviews: list[ReviewResult]
    query: str
    rewritten_query: str = ""
    timings: dict = {}


class StatsResponse(BaseModel):
    total_reviews: int
    average_rating: float
    category: str
    rating_distribution: dict
