import { useState, useEffect } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import ChatInterface from './components/ChatInterface'
import InsightPanel from './components/InsightPanel'

// Allow Vercel to inject the live backend URL, fallback to localhost for local dev
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [loadingStage, setLoadingStage] = useState('')
  const [currentAnalysis, setCurrentAnalysis] = useState(null)
  const [currentReviews, setCurrentReviews] = useState(null)
  const [stats, setStats] = useState(null)
  const [history, setHistory] = useState([])

  // Fetch dataset stats on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/stats`)
      .then((r) => r.json())
      .then(setStats)
      .catch(() => { })
  }, [])

  const handleSendQuery = async (query) => {
    // Add user message
    setMessages((prev) => [...prev, { role: 'user', content: query }])
    setIsLoading(true)
    setLoadingStage('Searching relevant reviews...')

    // Update history
    setHistory((prev) => {
      const updated = [query, ...prev.filter((q) => q !== query)]
      return updated.slice(0, 10)
    })

    try {
      setLoadingStage('Running 3-agent pipeline...')

      const response = await fetch(`${API_BASE}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 10 }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()

      // Add assistant message
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          timings: data.timings,
        },
      ])

      // Update insight panel
      setCurrentAnalysis(data.analysis)
      setCurrentReviews(data.reviews)
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Sorry, I encountered an error: ${err.message}. Make sure the backend is running on port 8000.`,
        },
      ])
    } finally {
      setIsLoading(false)
      setLoadingStage('')
    }
  }

  const handleHistoryClick = (query) => {
    if (!isLoading) {
      handleSendQuery(query)
    }
  }

  return (
    <div className="app-layout">
      <Sidebar
        stats={stats}
        history={history}
        onHistoryClick={handleHistoryClick}
      />
      <ChatInterface
        onSendQuery={handleSendQuery}
        messages={messages}
        isLoading={isLoading}
        loadingStage={loadingStage}
      />
      <InsightPanel
        analysis={currentAnalysis}
        reviews={currentReviews}
      />
    </div>
  )
}

export default App
