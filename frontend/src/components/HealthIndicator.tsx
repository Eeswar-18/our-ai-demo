import { useEffect, useState } from 'react'

const HealthIndicator = () => {
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking')
  const [auditLogsCount, setAuditLogsCount] = useState(0)
  const [lastAuditLog, setLastAuditLog] = useState<string | null>(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('/v1/health')
        if (response.ok) {
          setBackendStatus('connected')

          const logsResponse = await fetch('/v1/audit-logs?limit=1')
          if (logsResponse.ok) {
            const logsData = await logsResponse.json()
            setAuditLogsCount(logsData.count)
            if (logsData.logs.length > 0) {
              setLastAuditLog(logsData.logs[0].timestamp)
            }
          }
        } else {
          setBackendStatus('disconnected')
        }
      } catch {
        setBackendStatus('disconnected')
      }
    }

    checkHealth()
    const interval = setInterval(checkHealth, 5000)
    return () => clearInterval(interval)
  }, [])

  const statusText =
    backendStatus === 'connected'
      ? 'SYSTEM ONLINE'
      : backendStatus === 'disconnected'
        ? 'OFFLINE'
        : 'CHECKING'

  return (
    <div
      className="health-indicator"
      title={`Backend: ${backendStatus === 'connected' ? 'Online' : backendStatus === 'disconnected' ? 'Offline' : 'Checking...'}\nAudit Logs: ${auditLogsCount} entries\nLast Log: ${lastAuditLog ? new Date(lastAuditLog).toLocaleTimeString() : 'None'}`}
    >
      <div className={`health-dot ${backendStatus === 'connected' ? 'online' : backendStatus === 'disconnected' ? 'offline' : 'checking'}`} />
      <span>{statusText}</span>
    </div>
  )
}

export default HealthIndicator
