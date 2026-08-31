import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, HardHat, Download } from 'lucide-react'
import { LoadingState, EmptyState } from '../components/States.jsx'
import { safetyService } from '../services/safetyService.js'

export default function WorkerDetails() {
  const { id } = useParams()
  const [worker, setWorker] = useState(null)
  const [events, setEvents] = useState([])

  useEffect(() => {
    Promise.all([safetyService.getWorker(id), safetyService.getWorkerEvents(id)]).then(([w, e]) => {
      setWorker(w)
      setEvents(e)
    })
  }, [id])

  const handleDownloadZip = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8001/api/workers/${id}/export-evidence`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (!response.ok) throw new Error('Failed to download evidence')
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `evidence_${worker.full_name.replace(/\s+/g, '_')}.zip`
      document.body.appendChild(a)
      a.click()
      a.remove()
    } catch (err) {
      alert("Error exporting evidence: " + err.message)
    }
  }

  if (!worker) return <LoadingState label="Loading worker..." />

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/workers" className="p-2 rounded-md hover:bg-base-700 text-ink-500">
          <ArrowLeft size={18} />
        </Link>
        <div className="w-11 h-11 rounded-full bg-base-700 border border-base-500 flex items-center justify-center">
          <HardHat size={20} className="text-signal-amber" />
        </div>
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900">{worker.full_name}</h1>
          <p className="text-sm font-mono text-ink-500">
            {worker.worker_code} &middot; {worker.department} &middot; {worker.shift} shift
          </p>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-display font-semibold text-ink-900 text-sm uppercase tracking-wide">
            Violation History ({events.length})
          </h2>
          {events.length > 0 && (
            <button onClick={handleDownloadZip} className="btn btn-primary text-xs flex items-center gap-2 py-1.5 px-3">
              <Download size={14} /> Export Evidence (.zip)
            </button>
          )}
        </div>
        {events.length === 0 ? (
          <EmptyState title="Clean record" description="No safety violations recorded for this worker." />
        ) : (
          <div className="panel divide-y divide-base-600">
            {events.map((e) => (
              <div key={e.id} className="p-4 flex items-center justify-between gap-4">
                <div>
                  <div className="text-sm font-medium text-ink-900">{e.violation_type.replace('_', ' ')}</div>
                  <div className="text-[11px] font-mono text-ink-500 mt-0.5">
                    {new Date(e.timestamp).toLocaleString()} &middot; {e.duration_seconds}s duration
                  </div>
                </div>
                <span className="text-xs font-mono text-ink-500">{Math.round(e.confidence * 100)}% conf.</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
