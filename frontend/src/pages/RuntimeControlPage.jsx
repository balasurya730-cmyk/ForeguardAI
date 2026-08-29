import { useEffect, useState, useCallback } from 'react'
import RuntimeControl from '../components/RuntimeControl.jsx'
import { LoadingState, EmptyState } from '../components/States.jsx'
import { machineService } from '../services/machineService.js'
import { useWebSocketContext } from '../hooks/WebSocketContext.jsx'
import { useAuth } from '../hooks/useAuth.jsx'

export default function RuntimeControlPage() {
  const [machines, setMachines] = useState([])
  const [runtimes, setRuntimes] = useState({})
  const [loading, setLoading] = useState(true)
  const { on } = useWebSocketContext()
  const { user } = useAuth()
  const canManage = user?.role === 'ADMIN' || user?.role === 'MANAGER'

  const load = useCallback(async () => {
    const list = await machineService.list()
    setMachines(list)
    const entries = await Promise.all(list.map((m) => machineService.getRuntime(m.id).then((rt) => [m.id, rt])))
    setRuntimes(Object.fromEntries(entries))
    setLoading(false)
  }, [])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    return on('runtime_update', (data) => {
      setRuntimes((prev) => ({ ...prev, [data.machine_id]: data }))
    })
  }, [on])

  async function handleStart(machineId, durationSeconds) {
    const rt = await machineService.startRuntime(machineId, durationSeconds)
    setRuntimes((prev) => ({ ...prev, [machineId]: rt }))
  }

  async function handleStop(machineId) {
    const rt = await machineService.stopRuntime(machineId)
    setRuntimes((prev) => ({ ...prev, [machineId]: rt }))
  }

  if (loading) return <LoadingState label="Loading runtime status..." />

  if (!canManage) {
    return <EmptyState title="Manager access required" description="Only managers and admins can control machine runtime." />
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-900">Runtime Control</h1>
        <p className="text-sm text-ink-500 mt-0.5">Set duration, start, monitor, and stop machines remotely</p>
      </div>

      {machines.length === 0 ? (
        <EmptyState title="No machines to control" />
      ) : (
        <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {machines.map((m) => (
            <RuntimeControl
              key={m.id}
              machine={m}
              runtime={runtimes[m.id]}
              onStart={(duration) => handleStart(m.id, duration)}
              onStop={() => handleStop(m.id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
