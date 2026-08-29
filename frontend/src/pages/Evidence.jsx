import { useEffect, useState } from 'react'
import { ImageOff, Check } from 'lucide-react'
import { LoadingState, EmptyState } from '../components/States.jsx'
import { safetyService } from '../services/safetyService.js'

export default function Evidence() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [onlyUnreviewed, setOnlyUnreviewed] = useState(false)

  useEffect(() => {
    safetyService.listEvidence(200).then((data) => {
      setItems(data)
      setLoading(false)
    })
  }, [])

  async function handleMarkReviewed(id) {
    const updated = await safetyService.markReviewed(id)
    setItems((prev) => prev.map((i) => (i.id === id ? updated : i)))
  }

  const filtered = onlyUnreviewed ? items.filter((i) => !i.reviewed) : items

  if (loading) return <LoadingState label="Loading evidence..." />

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900">Evidence</h1>
          <p className="text-sm text-ink-500 mt-0.5">{items.length} captured events</p>
        </div>
        <label className="flex items-center gap-2 text-sm text-ink-500 cursor-pointer">
          <input type="checkbox" checked={onlyUnreviewed} onChange={(e) => setOnlyUnreviewed(e.target.checked)} className="accent-signal-cyan" />
          Show unreviewed only
        </label>
      </div>

      {filtered.length === 0 ? (
        <EmptyState title="No evidence found" />
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((item) => (
            <div key={item.id} className="panel overflow-hidden">
              <div className="aspect-video bg-base-900 flex items-center justify-center border-b border-base-600">
                {item.image_path ? (
                  <img
                    src={item.image_path}
                    alt={item.event_type}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none'
                      e.target.nextSibling.style.display = 'flex'
                    }}
                  />
                ) : null}
                <div className="hidden w-full h-full items-center justify-center text-ink-500" style={{ display: item.image_path ? 'none' : 'flex' }}>
                  <ImageOff size={28} />
                </div>
              </div>
              <div className="p-3.5">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-ink-900">{item.event_type.replace('_', ' ')}</span>
                  {item.reviewed ? (
                    <span className="badge-normal"><Check size={11} />Reviewed</span>
                  ) : (
                    <button onClick={() => handleMarkReviewed(item.id)} className="text-xs font-mono text-signal-cyan hover:underline">
                      Mark Reviewed
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-1 text-[11px] font-mono text-ink-500">
                  <div>Worker: {item.worker_id ? `#${item.worker_id}` : '—'}</div>
                  <div>Camera: {item.camera_id ? `C${String(item.camera_id).padStart(2, '0')}` : '—'}</div>
                  <div>Confidence: {item.confidence}%</div>
                  <div>{new Date(item.created_at).toLocaleDateString()}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
