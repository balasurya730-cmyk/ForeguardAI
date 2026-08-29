import { useEffect, useState } from 'react'
import AlertCard from '../components/AlertCard.jsx'
import { LoadingState, EmptyState } from '../components/States.jsx'
import { alertService } from '../services/alertService.js'
import { useWebSocketContext } from '../hooks/WebSocketContext.jsx'

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('ALL')
  const { on } = useWebSocketContext()

  useEffect(() => {
    alertService.list().then((data) => {
      setAlerts(data)
      setLoading(false)
    })
  }, [])

  useEffect(() => {
    return on('alert', (data) => {
      setAlerts((prev) => [data, ...prev])
    })
  }, [on])

  async function handleAcknowledge(id) {
    const updated = await alertService.acknowledge(id)
    setAlerts((prev) => prev.map((a) => (a.id === id ? updated : a)))
  }

  async function handleResolve(id) {
    const updated = await alertService.resolve(id)
    setAlerts((prev) => prev.map((a) => (a.id === id ? updated : a)))
  }

  const filtered = filter === 'ALL' ? alerts : alerts.filter((a) => a.status === filter)

  if (loading) return <LoadingState label="Loading alerts..." />

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900">Alerts</h1>
          <p className="text-sm text-ink-500 mt-0.5">Centralized alert engine &middot; {alerts.length} total</p>
        </div>
        <div className="flex gap-2">
          {['ALL', 'ACTIVE', 'ACKNOWLEDGED', 'RESOLVED'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-md text-xs font-mono transition ${
                filter === f ? 'bg-signal-cyan text-base-950' : 'bg-base-700 text-ink-500 hover:text-ink-900'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState title="No alerts" description="Everything looks quiet right now." />
      ) : (
        <div className="space-y-2">
          {filtered.map((a) => (
            <AlertCard key={a.id} alert={a} onAcknowledge={handleAcknowledge} onResolve={handleResolve} />
          ))}
        </div>
      )}
    </div>
  )
}
