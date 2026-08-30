import { useState, useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import ToolExecutionPanel from './ToolExecutionPanel'
import VerificationBadge from './VerificationBadge'
import HealthIndicator from './HealthIndicator'
import ExamplePrompts from './ExamplePrompts'

const ChatInterface = () => {
  const [messages, setMessages] = useState<Array<{ text: string; isUser: boolean }>>([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [toolExecutions, setToolExecutions] = useState<Array<unknown>>([])
  const [verificationResults, setVerificationResults] = useState<Array<{ goal_achieved: boolean; reason: string }>>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, toolExecutions, verificationResults])

  const sendMessage = async () => {
    if (!inputValue.trim() || loading) return

    const userMessage = inputValue
    setInputValue('')
    setLoading(true)

    setMessages(prev => [...prev, { text: userMessage, isUser: true }])

    try {
      const response = await fetch('/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userMessage })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      setMessages(prev => [...prev, { text: data.message, isUser: false }])
      setToolExecutions(data.tool_executions || [])
      setVerificationResults(data.verification_results || [])
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [...prev, { text: 'Sorry, something went wrong. Please try again.', isUser: false }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleExampleClick = (prompt: string) => {
    setInputValue(prompt)
  }

  return (
    <div className="chat-page">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-left">
          <a href="/" className="back-btn">← Home</a>
          <div>
            <h2 className="chat-header-title">AI Business Assistant</h2>
            <p className="chat-header-subtitle">Demo Mode</p>
          </div>
        </div>
        <HealthIndicator />
      </div>

      {/* Main content */}
      <div className="chat-main">
        {/* Conversation area */}
        <div className="chat-conversation">
          {messages.length === 0 && toolExecutions.length === 0 && verificationResults.length === 0 && (
            <ExamplePrompts onExampleClick={handleExampleClick} />
          )}

          <div>
            {messages.map((msg, index) => (
              <MessageBubble key={index} message={msg.text} isUser={msg.isUser} />
            ))}
            {loading && (
              <MessageBubble message="AI is thinking..." isUser={false} isThinking />
            )}
          </div>
          <div ref={messagesEndRef} />
        </div>

        {/* Sidebar for tools and verification */}
        {(toolExecutions.length > 0 || verificationResults.length > 0) && (
          <div className="chat-sidebar">
            {toolExecutions.length > 0 && (
              <div className="chat-sidebar-section">
                <div className="chat-sidebar-title">
                  <span>Tool Executions</span>
                  <span className="chat-sidebar-count">{toolExecutions.length}</span>
                </div>
                {toolExecutions.map((exec, index) => (
                  <ToolExecutionPanel key={index} execution={exec} />
                ))}
              </div>
            )}

            {verificationResults.length > 0 && (
              <div className="chat-sidebar-section">
                <div className="chat-sidebar-title">
                  <span>Verification Results</span>
                  <span className="chat-sidebar-count">{verificationResults.length}</span>
                </div>
                {verificationResults.map((ver, index) => (
                  <VerificationBadge key={index} verification={ver} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="chat-input-wrapper">
        <div className="chat-input-container">
          <textarea
            className="chat-input"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about payments, subscriptions, plans..."
            disabled={loading}
            rows={1}
          />
          <button
            className="chat-send-btn"
            onClick={sendMessage}
            disabled={loading || !inputValue.trim()}
          >
            {loading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface
