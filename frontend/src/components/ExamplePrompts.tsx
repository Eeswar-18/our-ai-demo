interface ExamplePromptsProps {
  onExampleClick: (prompt: string) => void
}

const prompts = [
  "What plans do you offer?",
  "I was charged twice for transaction txn_123456.",
  "My subscription is inactive. Can you reactivate it?",
  "What is your refund policy?"
]

const ExamplePrompts = ({ onExampleClick }: ExamplePromptsProps) => {
  return (
    <div className="example-prompts">
      <div className="example-prompts-label">Try a question</div>
      <div className="example-prompts-grid">
        {prompts.map((prompt, index) => (
          <button
            key={index}
            className="example-prompt"
            onClick={() => onExampleClick(prompt)}
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  )
}

export default ExamplePrompts
