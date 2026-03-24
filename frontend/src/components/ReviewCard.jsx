import { useState } from 'react'

export default function ReviewCard({ review }) {
    const [expanded, setExpanded] = useState(false)

    const stars = '★'.repeat(Math.round(review.rating)) + '☆'.repeat(5 - Math.round(review.rating))

    return (
        <div className="review-card">
            <div className="review-card-header">
                <span className="review-stars">{stars}</span>
                <span className="review-score">{(review.score * 100).toFixed(0)}% match</span>
            </div>
            <div className="review-title">{review.title || 'Untitled Review'}</div>
            <div className={`review-text ${expanded ? 'expanded' : ''}`}>
                {review.text || 'No review text available.'}
            </div>
            {review.text && review.text.length > 150 && (
                <button className="review-expand" onClick={() => setExpanded(!expanded)}>
                    {expanded ? '▲ Show less' : '▼ Read more'}
                </button>
            )}
            <div className="review-footer">
                {review.verified_purchase && (
                    <span className="review-badge">✓ Verified</span>
                )}
                {review.helpful_vote > 0 && (
                    <span>👍 {review.helpful_vote} helpful</span>
                )}
            </div>
        </div>
    )
}
