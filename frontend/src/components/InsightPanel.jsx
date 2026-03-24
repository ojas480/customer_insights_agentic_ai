import ReviewCard from './ReviewCard'

export default function InsightPanel({ analysis, reviews }) {
    if (!analysis || !reviews) {
        return (
            <div className="insight-panel">
                <div className="insight-empty">
                    <div className="insight-empty-icon">📊</div>
                    <p>Ask a question to see analysis and matching reviews here</p>
                </div>
            </div>
        )
    }

    const sentiment = analysis.sentiment || {}
    const ratingDist = analysis.rating_summary?.distribution || {}
    const totalRatings = Object.values(ratingDist).reduce((a, b) => a + b, 0) || 1

    // Build conic-gradient for donut
    const pos = sentiment.positive_pct || 0
    const neg = sentiment.negative_pct || 0
    const mix = sentiment.mixed_pct || 0
    const donutStyle = {
        background: `conic-gradient(
      #10b981 0% ${pos}%,
      #ef4444 ${pos}% ${pos + neg}%,
      #f59e0b ${pos + neg}% ${pos + neg + mix}%,
      rgba(255,255,255,0.05) ${pos + neg + mix}% 100%
    )`,
        mask: 'radial-gradient(farthest-side, transparent 60%, #000 61%)',
        WebkitMask: 'radial-gradient(farthest-side, transparent 60%, #000 61%)',
    }

    return (
        <div className="insight-panel">
            <div className="insight-panel-header">📊 Analysis</div>

            {/* Sentiment */}
            <div className="insight-section">
                <div className="insight-section-title">Sentiment</div>
                <div className="sentiment-display">
                    <div className="sentiment-donut" style={donutStyle}>
                        <div className="sentiment-donut-center">
                            {sentiment.overall === 'positive' ? '😊' : sentiment.overall === 'negative' ? '😞' : '😐'}
                        </div>
                    </div>
                    <div className="sentiment-labels">
                        <div className="sentiment-label">
                            <span className="sentiment-dot positive"></span>
                            Positive: {pos}%
                        </div>
                        <div className="sentiment-label">
                            <span className="sentiment-dot negative"></span>
                            Negative: {neg}%
                        </div>
                        <div className="sentiment-label">
                            <span className="sentiment-dot mixed"></span>
                            Mixed: {mix}%
                        </div>
                    </div>
                </div>
            </div>

            {/* Pros / Cons */}
            {(analysis.pros?.length > 0 || analysis.cons?.length > 0) && (
                <div className="insight-section">
                    <div className="insight-section-title">Pros & Cons</div>
                    <div className="pros-cons-grid">
                        <div className="pros-list">
                            <div className="pros-list-title">👍 Pros</div>
                            {(analysis.pros || []).map((p, i) => (
                                <div key={i} className="pros-item">{p}</div>
                            ))}
                        </div>
                        <div className="cons-list">
                            <div className="cons-list-title">👎 Cons</div>
                            {(analysis.cons || []).map((c, i) => (
                                <div key={i} className="cons-item">{c}</div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Themes */}
            {analysis.themes?.length > 0 && (
                <div className="insight-section">
                    <div className="insight-section-title">Key Themes</div>
                    <div className="themes-container">
                        {analysis.themes.map((t, i) => (
                            <span key={i} className="theme-tag">{t}</span>
                        ))}
                    </div>
                </div>
            )}

            {/* Rating Distribution */}
            {Object.keys(ratingDist).length > 0 && (
                <div className="insight-section">
                    <div className="insight-section-title">Rating Distribution</div>
                    <div className="rating-bars">
                        {[5, 4, 3, 2, 1].map((star) => {
                            const count = ratingDist[String(star)] || 0
                            const pct = (count / totalRatings) * 100
                            return (
                                <div key={star} className="rating-bar-row">
                                    <span className="rating-bar-label">{star}★</span>
                                    <div className="rating-bar-track">
                                        <div className="rating-bar-fill" style={{ width: `${pct}%` }}></div>
                                    </div>
                                    <span className="rating-bar-count">{count}</span>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}

            {/* Matching Reviews */}
            {reviews.length > 0 && (
                <div className="reviews-section">
                    <div className="reviews-section-title">Matching Reviews ({reviews.length})</div>
                    {reviews.slice(0, 5).map((r, i) => (
                        <ReviewCard key={i} review={r} />
                    ))}
                </div>
            )}
        </div>
    )
}
