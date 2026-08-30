const capabilities = [
  {
    icon: '◈',
    title: 'AI Customer Support',
    description: 'Answers business and customer questions using the business\'s own context and knowledge base.'
  },
  {
    icon: '⬡',
    title: 'Payment Intelligence',
    description: 'Checks payment information, transaction history, and billing details through integrated business tools.'
  },
  {
    icon: '◇',
    title: 'Subscription Management',
    description: 'Checks and handles subscription-related requests with automated verification and execution.'
  },
  {
    icon: '▣',
    title: 'Business Knowledge',
    description: 'Uses the business\'s own context, policies, and information for accurate, contextual responses.'
  },
  {
    icon: '◎',
    title: 'Verified Actions',
    description: 'Does not merely claim that an action succeeded. Tool execution and verification results are available for every operation.'
  }
]

const Capabilities = () => {
  return (
    <section className="capabilities-section" id="capabilities">
      <div className="capabilities-header">
        <div className="capabilities-label">What it does</div>
        <h2 className="capabilities-title">Capabilities</h2>
        <p className="capabilities-subtitle">
          A complete AI business assistant with real tool execution, verification, and contextual intelligence.
        </p>
      </div>

      <div className="capabilities-grid">
        {capabilities.map((cap, index) => (
          <div key={index} className="capability-card">
            <div className="capability-icon">{cap.icon}</div>
            <h3>{cap.title}</h3>
            <p>{cap.description}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

export default Capabilities
