import { useState, useRef, useEffect } from 'react'

const SUGGESTIONS = [
  "What are the best products for hair care?",
  "Show me reviews for moisturizers",
  "What do people complain about most?",
  "Best rated beauty products?",
  "Products with the most helpful reviews?",
]

export default function ChatInterface({ onSendQuery, messages, isLoading, loadingStage }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    onSendQuery(input.trim())
    setInput('')
  }

  const handleSuggestion = (text) => {
    if (isLoading) return
    onSendQuery(text)
  }

  return (
    <div className="chat-area">
      <div className="chat-messages">
        {messages.length === 0 && !isLoading ? (
          <div className="welcome-screen">
            <div className="welcome-icon">🔍</div>
            <h2>CustomerInsight</h2>
            <p>
              Ask me anything about beauty products. I'll search through 15,000+ Amazon reviews 
              using AI to find relevant insights, sentiment analysis, and recommendations.
            </p>
            <div className="suggestion-chips">
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  className="suggestion-chip"
                  onClick={() => handleSuggestion(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, i) => (
              <div key={i} className={`message message-${msg.role}`}>
                <div className="message-label">
                  {msg.role === 'user' ? 'You' : '🤖 CustomerInsight'}
                </div>
                <div className="message-content">{msg.content}</div>
                {msg.timings && (
                  <div className="timings-bar">
                    <div className="timing-item">
                      🔍 Retriever: <span className="timing-value">{msg.timings.retriever}s</span>
                    </div>
                    <div className="timing-item">
                      📊 Analyzer: <span className="timing-value">{msg.timings.analyzer}s</span>
                    </div>
                    <div className="timing-item">
                      ✍️ Summarizer: <span className="timing-value">{msg.timings.summarizer}s</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="loading-message">
                <div className="message-label">🤖 CustomerInsight</div>
                <div className="loading-dots">
                  <div className="loading-dots-inner">
                    <div className="loading-dot"></div>
                    <div className="loading-dot"></div>
                    <div className="loading-dot"></div>
                  </div>
                  <span className="loading-label">Analyzing reviews...</span>
                </div>
                {loadingStage && (
                  <div className="loading-stage">⚙️ {loadingStage}</div>
                )}
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <form onSubmit={handleSubmit}>
          <div className="chat-input-wrapper">
            <input
              className="chat-input"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about products, reviews, or trends..."
              disabled={isLoading}
            />
            <button
              className="send-button"
              type="submit"
              disabled={!input.trim() || isLoading}
            >
              ➤
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
