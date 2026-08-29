import { useEffect, useState } from 'react'
import WorkerCard from '../components/WorkerCard.jsx'
import { LoadingState, EmptyState } from '../components/States.jsx'
import { safetyService } from '../services/safetyService.js'

export default function Workers() {
  const [workers, setWorkers] = useState([])
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    Promise.all([safetyService.listWorkers(), safetyService.listEvents(500)]).then(([w, e]) => {
      setWorkers(w)
      setEvents(e)
      setLoading(false)
    })
  }, [])

  const violationCounts = events.reduce((acc, e) => {
    if (e.worker_id) acc[e.worker_id] = (acc[e.worker_id] || 0) + 1
    return acc
  }, {})

  const filtered = workers.filter(
    (w) =>
      w.full_name.toLowerCase().includes(search.toLowerCase()) ||
      w.worker_code.toLowerCase().includes(search.toLowerCase())
  )

  if (loading) return <LoadingState label="Loading workers..." />

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900">Workers</h1>
          <p className="text-sm text-ink-500 mt-0.5">{workers.length} workers monitored</p>
        </div>
        <input
          className="input-field w-full sm:w-64"
          placeholder="Search by name or code..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState title="No workers found" />
      ) : (
        <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-3">
          {filtered.map((w) => (
            <WorkerCard key={w.id} worker={w} violationCount={violationCounts[w.id] || 0} />
          ))}
        </div>
      )}
    </div>
  )
}
