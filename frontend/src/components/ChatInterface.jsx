import { useState, useEffect, useRef } from 'react'
import ChatMessage from './ChatMessage'

export default function ChatInterface({ fileId, filename }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [logs, setLogs] = useState([])
  const [showSuccess, setShowSuccess] = useState(true)
  const [isAnalyzing, setIsAnalyzing] = useState(true)
  const messagesEndRef = useRef(null)
  const wsRef = useRef(null)

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }

  useEffect(scrollToBottom, [messages, logs])

  useEffect(() => {
    setTimeout(() => setShowSuccess(false), 2500)
  }, [])

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const ws = new WebSocket(`${protocol}//${host}/ws/${fileId}`)

    ws.onopen = () => {
      setLogs((prev) => [...prev, 'Connected'])
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'log') {
        setLogs((prev) => [...prev, data.message])
      } else if (data.type === 'result') {
        setMessages((prev) => [
          ...prev,
          {
            type: 'agent',
            content: data.content,
            image: data.image,
            plotly_figures: data.plotly_figures || [],
          },
        ])
        setLoading(false)
        setIsAnalyzing(false)
        setLogs([])
      } else if (data.type === 'error') {
        setMessages((prev) => [
          ...prev,
          { type: 'agent', content: `❌ Error: ${data.content}` },
        ])
        setLoading(false)
        setIsAnalyzing(false)
        setLogs([])
      }
    }

    ws.onclose = () => console.log('Disconnected')
    wsRef.current = ws

    return () => ws.close()
  }, [fileId])

  const sendMessage = () => {
    if (!input.trim() || loading) return

    const userMsg = { type: 'user', content: input }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)
    setLogs(['Processing...'])

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ message: userMsg.content }))
    } else {
      setMessages((prev) => [
        ...prev,
        { type: 'agent', content: '❌ WebSocket not connected' },
      ])
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-[700px] glass rounded-2xl shadow-2xl overflow-hidden relative border border-gold-500/20">
      {showSuccess && (
        <div
          className="absolute top-4 left-1/2 z-50 success-banner"
          style={{ transform: 'translateX(-50%)' }}
        >
          <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-xl shadow-2xl flex items-center space-x-3 animate-bounce border border-green-400/30">
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span className="font-bold">✨ Data Loaded Successfully!</span>
          </div>
        </div>
      )}

      <div className="bg-zinc-900 border-b border-gold-500/20 px-6 py-4 flex justify-between items-center">
        <div>
          <h2 className="text-gold-400 font-bold text-lg">Data Analysis Chat</h2>
          <p className="text-zinc-500 text-sm">File: {filename}</p>
        </div>
        <div className="h-2 w-2 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]"></div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 bg-zinc-950 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-zinc-900">
        {isAnalyzing && messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full">
            <div className="glass border border-gold-500/30 rounded-2xl p-8 max-w-md text-center shadow-[0_0_30px_rgba(255,193,7,0.05)]">
              <div className="pulse-icon mb-4">
                <svg
                  className="w-16 h-16 text-gold-500 mx-auto"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <p className="text-xl font-bold text-gold-400 mb-2">
                Analyzing Your Data
              </p>
              <p className="text-sm text-zinc-400 mb-4">
                Generating intelligent insights...
              </p>
              <div className="flex items-center justify-center space-x-2">
                <div
                  className="w-2 h-2 bg-gold-500 rounded-full animate-bounce"
                  style={{ animationDelay: '0s' }}
                ></div>
                <div
                  className="w-2 h-2 bg-gold-500 rounded-full animate-bounce"
                  style={{ animationDelay: '0.2s' }}
                ></div>
                <div
                  className="w-2 h-2 bg-gold-500 rounded-full animate-bounce"
                  style={{ animationDelay: '0.4s' }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <ChatMessage key={idx} message={msg} />
        ))}

        {loading && (
          <div className="flex justify-start mb-4">
            <div className="bg-zinc-900 border-l-2 border-gold-500 rounded-r-xl rounded-bl-xl p-4 max-w-md shadow-lg">
              <p className="font-bold text-gold-500 mb-2 flex items-center text-xs uppercase tracking-wider">
                <span className="animate-pulse mr-2">●</span>
                Agent Processing
              </p>
              <div className="text-sm text-zinc-400 font-mono space-y-1">
                {logs.map((log, idx) => (
                  <div key={idx} className="animate-pulse">
                    ▸ {log}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="p-5 bg-zinc-900 border-t border-gold-500/20">
        <div className="flex space-x-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about your data..."
            className="flex-1 px-5 py-3 rounded-xl bg-zinc-950 border border-zinc-700 text-zinc-200 focus:outline-none focus:border-gold-500/50 focus:ring-1 focus:ring-gold-500/50 transition-all placeholder-zinc-600"
            disabled={loading || isAnalyzing}
          />
          <button
            onClick={sendMessage}
            disabled={loading || isAnalyzing}
            className="px-8 py-3 bg-gradient-to-r from-gold-600 to-gold-500 text-black font-bold rounded-xl hover:shadow-[0_0_15px_rgba(255,193,7,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}