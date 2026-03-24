export default function Sidebar({ stats, history, onHistoryClick }) {
    return (
        <div className="sidebar">
            {/* Logo */}
            <div className="sidebar-logo">
                <div className="sidebar-logo-icon">🔍</div>
                <h1>CustomerInsight</h1>
            </div>

            {/* Dataset Stats */}
            <div className="sidebar-section">
                <div className="sidebar-section-title">Dataset</div>
                <div className="stat-card glass">
                    <div className="stat-label">📄 Total Reviews</div>
                    <div className="stat-value gradient">
                        {stats?.total_reviews?.toLocaleString() || '...'}
                    </div>
                </div>
                <div className="stat-card glass">
                    <div className="stat-label">⭐ Average Rating</div>
                    <div className="stat-value">
                        {stats?.average_rating ? `${stats.average_rating} / 5.0` : '...'}
                    </div>
                </div>
                <div className="stat-card glass">
                    <div className="stat-label">🏷️ Category</div>
                    <div className="stat-value" style={{ fontSize: '16px' }}>
                        {stats?.category || '...'}
                    </div>
                </div>
            </div>

            {/* History */}
            {history.length > 0 && (
                <div className="sidebar-section">
                    <div className="sidebar-section-title">Recent Queries</div>
                    {history.map((q, i) => (
                        <div
                            key={i}
                            className="history-item"
                            onClick={() => onHistoryClick(q)}
                            title={q}
                        >
                            💬 {q}
                        </div>
                    ))}
                </div>
            )}

            {/* About */}
            <div className="sidebar-about">
                <strong>3-Agent Architecture</strong><br />
                1️⃣ Retriever — FAISS + MiniLM search<br />
                2️⃣ Analyzer — Sentiment & patterns<br />
                3️⃣ Summarizer — Natural language response<br /><br />
                <strong>Tech Stack</strong><br />
                RAG Pipeline • FAISS • MiniLM • GPT-4o-mini • FastAPI • React
            </div>
        </div>
    )
}
