interface MessageBubbleProps {
  message: string
  isUser: boolean
  isThinking?: boolean
}

const MessageBubble = ({ message, isUser, isThinking = false }: MessageBubbleProps) => {
  return (
    <div className={`message ${isUser ? 'user' : 'assistant'}${isThinking ? ' thinking' : ''}`}>
      <div className="message-bubble">
        {message}
      </div>
    </div>
  )
}

export default MessageBubble
