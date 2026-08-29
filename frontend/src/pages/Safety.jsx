import { useEffect, useState } from 'react'
import { ShieldAlert, Smartphone, HardHat, ImageOff } from 'lucide-react'
import { LoadingState, EmptyState } from '../components/States.jsx'
import { safetyService } from '../services/safetyService.js'
import { useWebSocketContext } from '../hooks/WebSocketContext.jsx'

const TYPE_ICON = { NO_HELMET: HardHat, NO_PPE: ShieldAlert, MOBILE_USAGE: Smartphone }
const TYPE_LABEL = { NO_HELMET: 'Helmet Not Detected', NO_PPE: 'PPE Missing', MOBILE_USAGE: 'Mobile Usage' }

export default function Safety() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('ALL')
  const [selectedEvidence, setSelectedEvidence] = useState(null)
  const { on } = useWebSocketContext()

  useEffect(() => {
    safetyService.listEvents(200).then((data) => {
      setEvents(data)
      setLoading(false)
    })
  }, [])

  useEffect(() => {
    return on('safety_event', (data) => {
      setEvents((prev) => [data, ...prev])
    })
  }, [on])

  const filtered = filter === 'ALL' ? events : events.filter((e) => e.violation_type === filter)

  if (loading) return <LoadingState label="Loading safety events..." />

  return (
    <div className="space-y-6">
      {selectedEvidence && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-base-950/80 backdrop-blur-sm p-4" onClick={() => setSelectedEvidence(null)}>
          <div className="bg-base-900 border border-base-600 rounded-lg overflow-hidden max-w-2xl w-full shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="p-3 border-b border-base-600 flex justify-between items-center bg-base-800">
              <h3 className="font-display font-semibold text-sm text-ink-900">Photographic Evidence</h3>
              <button onClick={() => setSelectedEvidence(null)} className="text-ink-500 hover:text-ink-900 text-lg leading-none">&times;</button>
            </div>
            <div className="aspect-video bg-base-950 flex items-center justify-center relative">
              <img
                src={selectedEvidence}
                alt="Evidence"
                className="w-full h-full object-contain"
                onError={(ev) => {
                  ev.target.style.display = 'none'
                  ev.target.nextSibling.style.display = 'flex'
                }}
              />
              <div className="hidden w-full h-full items-center justify-center text-ink-500 absolute inset-0">
                <ImageOff size={28} />
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900">Safety Monitoring</h1>
          <p className="text-sm text-ink-500 mt-0.5">YOLO + ByteTrack detection feed &middot; {events.length} events</p>
        </div>
        <div className="flex gap-2">
          {['ALL', 'NO_HELMET', 'NO_PPE', 'MOBILE_USAGE'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-md text-xs font-mono transition ${
                filter === f ? 'bg-signal-cyan text-base-950' : 'bg-base-700 text-ink-500 hover:text-ink-900'
              }`}
            >
              {f.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState title="No violations detected" description="The camera feed hasn't flagged any safety issues." />
      ) : (
        <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((e) => {
            const Icon = TYPE_ICON[e.violation_type] || ShieldAlert
            return (
              <div key={e.id} className="panel overflow-hidden">
                <div className="p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Icon size={16} className="text-signal-amber" />
                    <span className="font-medium text-sm text-ink-900">{TYPE_LABEL[e.violation_type]}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs font-mono text-ink-500 mb-2">
                    <div>Worker: {e.worker_id ? `#${e.worker_id}` : '—'}</div>
                    <div>Camera: {e.camera_id ? `C${String(e.camera_id).padStart(2, '0')}` : '—'}</div>
                    <div>Confidence: {Math.round(e.confidence * 100)}%</div>
                    <div>Duration: {e.duration_seconds}s</div>
                  </div>
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-base-600/50">
                    <div className="text-[11px] font-mono text-ink-500">{new Date(e.timestamp).toLocaleString()}</div>
                    {e.evidence_path && (
                      <button 
                        onClick={() => setSelectedEvidence(e.evidence_path)}
                        className="text-[11px] font-mono text-signal-cyan hover:underline flex items-center gap-1 bg-signal-cyan/10 px-2 py-1 rounded"
                      >
                        View Evidence
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
