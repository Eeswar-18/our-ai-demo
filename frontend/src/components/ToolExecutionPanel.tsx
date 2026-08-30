import { useState } from 'react'

interface ToolExecution {
  tool_name: string
  success: boolean
  parameters: unknown
  result: unknown
  error?: string
}

const ToolExecutionPanel = ({ execution }: { execution: unknown }) => {
  const [expanded, setExpanded] = useState(false)
  const exec = execution as ToolExecution

  const statusClass = exec.success ? 'success' : 'failed'

  return (
    <div className="tool-panel">
      <div className="tool-panel-header" onClick={() => setExpanded(!expanded)}>
        <div className="tool-panel-info">
          <div className={`tool-panel-status ${statusClass}`}>
            {exec.success ? '✓' : '✗'}
          </div>
          <span className="tool-panel-name">{exec.tool_name}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className={`tool-panel-status-text ${statusClass}`}>
            {exec.success ? 'SUCCESS' : 'FAILED'}
          </span>
          <span className={`tool-panel-chevron${expanded ? ' expanded' : ''}`}>
            ▼
          </span>
        </div>
      </div>

      {expanded && (
        <div className="tool-panel-details">
          <div className="tool-panel-section">
            <div className="tool-panel-label">Parameters</div>
            <pre className="tool-panel-pre">{JSON.stringify(exec.parameters, null, 2)}</pre>
          </div>
          <div className="tool-panel-section">
            <div className="tool-panel-label">Result</div>
            {exec.success ? (
              <pre className="tool-panel-pre">{JSON.stringify(exec.result, null, 2)}</pre>
            ) : (
              <p className="tool-panel-error">{exec.error}</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ToolExecutionPanel
