import { useEffect, useState } from 'react'
import { 
  ShieldAlert, Smartphone, HardHat, ImageOff, ShieldCheck, 
  User, Cog, Filter, Wrench, Eye, Shirt, Headphones, Shield
} from 'lucide-react'
import { LoadingState, EmptyState } from '../components/States.jsx'
import { safetyService } from '../services/safetyService.js'
import { useWebSocketContext } from '../hooks/WebSocketContext.jsx'

const TYPE_CONFIG = {
  // Compliant
  HELMET: { label: 'Helmet', icon: HardHat, color: 'text-signal-green' },
  GLOVES: { label: 'Gloves', icon: ShieldCheck, color: 'text-signal-green' },
  BOOTS: { label: 'Boots', icon: ShieldCheck, color: 'text-signal-green' },
  GLASSES: { label: 'Glasses', icon: Eye, color: 'text-signal-green' },
  SAFETY_VEST: { label: 'Safety Vest', icon: Shirt, color: 'text-signal-green' },
  FACE_MASK: { label: 'Face Mask', icon: ShieldCheck, color: 'text-signal-green' },
  FACE_SHIELD: { label: 'Face Shield', icon: Shield, color: 'text-signal-green' },
  EARMUFFS: { label: 'Earmuffs', icon: Headphones, color: 'text-signal-green' },

  // Hazards
  NO_HELMET: { label: 'NO Helmet', icon: ShieldAlert, color: 'text-signal-red' },
  NO_GLOVES: { label: 'NO Gloves', icon: ShieldAlert, color: 'text-signal-red' },
  NO_BOOTS: { label: 'NO Boots', icon: ShieldAlert, color: 'text-signal-red' },
  NO_GLASSES: { label: 'NO Glasses', icon: ShieldAlert, color: 'text-signal-red' },
  NO_SAFETY_VEST: { label: 'NO Safety Vest', icon: ShieldAlert, color: 'text-signal-red' },
  MOBILE_PHONE: { label: 'Mobile Phone', icon: Smartphone, color: 'text-signal-red' },

  // Neutral / Entities
  PERSON: { label: 'Person', icon: User, color: 'text-ink-500' },
  TOOLS: { label: 'Tools', icon: Wrench, color: 'text-ink-500' },
  MACHINE: { label: 'Machine', icon: Cog, color: 'text-ink-500' },
  MACHINE_GUARD: { label: 'Machine Guard', icon: Shield, color: 'text-ink-500' },
  UNIFORM: { label: 'Uniform', icon: Shirt, color: 'text-ink-500' },
}

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

  if (loading) return <LoadingState label="Loading detections..." />

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
          <h1 className="font-display text-2xl font-semibold text-ink-900">Safety & Detections</h1>
          <p className="text-sm text-ink-500 mt-0.5">YOLO 19-Class Custom Detection Feed &middot; {events.length} logs</p>
        </div>
        <div className="flex items-center gap-2">
          <Filter size={16} className="text-ink-500" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="input-field py-1.5 text-xs bg-base-900 appearance-none"
          >
            <option value="ALL">All Detections</option>
            <optgroup label="Hazards">
              <option value="NO_HELMET">NO Helmet</option>
              <option value="NO_GLOVES">NO Gloves</option>
              <option value="NO_BOOTS">NO Boots</option>
              <option value="NO_GLASSES">NO Glasses</option>
              <option value="NO_SAFETY_VEST">NO Safety Vest</option>
              <option value="MOBILE_PHONE">Mobile Phone</option>
            </optgroup>
            <optgroup label="Compliant PPE">
              <option value="HELMET">Helmet</option>
              <option value="GLOVES">Gloves</option>
              <option value="BOOTS">Boots</option>
              <option value="GLASSES">Glasses</option>
              <option value="SAFETY_VEST">Safety Vest</option>
              <option value="FACE_MASK">Face Mask</option>
              <option value="FACE_SHIELD">Face Shield</option>
              <option value="EARMUFFS">Earmuffs</option>
            </optgroup>
            <optgroup label="Objects / Entities">
              <option value="PERSON">Person</option>
              <option value="TOOLS">Tools</option>
              <option value="MACHINE">Machine</option>
              <option value="MACHINE_GUARD">Machine Guard</option>
              <option value="UNIFORM">Uniform</option>
            </optgroup>
          </select>
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState title="No detections logged" description="The camera feed hasn't flagged any events." />
      ) : (
        <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((e) => {
            const config = TYPE_CONFIG[e.violation_type] || { label: e.violation_type, icon: ShieldAlert, color: 'text-signal-amber' }
            const Icon = config.icon
            return (
              <div key={e.id} className="panel overflow-hidden">
                <div className="p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Icon size={16} className={config.color} />
                    <span className="font-medium text-sm text-ink-900">{config.label}</span>
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
