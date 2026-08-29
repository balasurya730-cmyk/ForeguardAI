import { useEffect, useState, useCallback } from 'react'
import { Plus, X, Settings2 } from 'lucide-react'
import GasZoneCard from '../components/GasZoneCard.jsx'
import { LoadingState } from '../components/States.jsx'
import { gasService } from '../services/gasService.js'
import { useWebSocketContext } from '../hooks/WebSocketContext.jsx'
import { useAuth } from '../hooks/useAuth.jsx'

export default function GasMonitoring() {
  const [zones, setZones] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingZone, setEditingZone] = useState(null)
  const { on } = useWebSocketContext()
  const { user } = useAuth()
  const canManage = user?.role === 'ADMIN' || user?.role === 'MANAGER'

  const load = useCallback(async () => {
    const data = await gasService.listZones()
    setZones(data)
    setLoading(false)
  }, [])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    return on('gas_update', (data) => {
      setZones((prev) => prev.map((z) => (z.id === data.id ? { ...z, ...data } : z)))
    })
  }, [on])

  if (loading) return <LoadingState label="Loading gas zones..." />

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900">Gas Monitoring</h1>
          <p className="text-sm text-ink-500 mt-0.5">{zones.length} zones configured</p>
        </div>
        {canManage && (
          <button onClick={() => setShowForm((v) => !v)} className="btn-primary flex items-center gap-2">
            {showForm ? <X size={16} /> : <Plus size={16} />}
            {showForm ? 'Cancel' : 'Add Zone'}
          </button>
        )}
      </div>

      {showForm && <ZoneForm onSaved={() => { setShowForm(false); load() }} />}

      <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {zones.map((z) => (
          <div key={z.id} className="relative group">
            <GasZoneCard zone={z} />
            {canManage && (
              <button
                onClick={() => setEditingZone(z)}
                className="absolute top-4 right-4 p-1.5 rounded-md bg-base-900/80 text-ink-500 hover:text-signal-cyan opacity-0 group-hover:opacity-100 transition"
              >
                <Settings2 size={14} />
              </button>
            )}
          </div>
        ))}
      </div>

      {editingZone && (
        <ZoneEditModal zone={editingZone} onClose={() => setEditingZone(null)} onSaved={() => { setEditingZone(null); load() }} />
      )}
    </div>
  )
}

function ZoneForm({ onSaved }) {
  const [form, setForm] = useState({ zone_name: '', gas_type: 'LPG', warning_threshold: 300, critical_threshold: 600 })
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      await gasService.createZone({
        ...form,
        warning_threshold: Number(form.warning_threshold),
        critical_threshold: Number(form.critical_threshold),
      })
      onSaved()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not create zone.')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="panel p-4 grid sm:grid-cols-5 gap-3 items-end">
      <Field label="Zone Name">
        <input required className="input-field w-full" value={form.zone_name} onChange={(e) => setForm({ ...form, zone_name: e.target.value })} placeholder="ZONE D" />
      </Field>
      <Field label="Gas Type">
        <input required className="input-field w-full" value={form.gas_type} onChange={(e) => setForm({ ...form, gas_type: e.target.value })} placeholder="LPG / CO" />
      </Field>
      <Field label="Warning (ppm)">
        <input type="number" required className="input-field w-full" value={form.warning_threshold} onChange={(e) => setForm({ ...form, warning_threshold: e.target.value })} />
      </Field>
      <Field label="Critical (ppm)">
        <input type="number" required className="input-field w-full" value={form.critical_threshold} onChange={(e) => setForm({ ...form, critical_threshold: e.target.value })} />
      </Field>
      <button type="submit" className="btn-primary">Create Zone</button>
      {error && <div className="text-signal-red text-sm sm:col-span-5">{error}</div>}
    </form>
  )
}

function ZoneEditModal({ zone, onClose, onSaved }) {
  const [form, setForm] = useState({
    gas_type: zone.gas_type,
    warning_threshold: zone.warning_threshold,
    critical_threshold: zone.critical_threshold,
  })

  async function handleSubmit(e) {
    e.preventDefault()
    await gasService.updateZone(zone.id, {
      ...form,
      warning_threshold: Number(form.warning_threshold),
      critical_threshold: Number(form.critical_threshold),
    })
    onSaved()
  }

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <form onSubmit={handleSubmit} onClick={(e) => e.stopPropagation()} className="panel p-5 w-full max-w-sm space-y-3">
        <h3 className="font-display font-semibold text-ink-900">Configure {zone.zone_name}</h3>
        <Field label="Gas Type">
          <input className="input-field w-full" value={form.gas_type} onChange={(e) => setForm({ ...form, gas_type: e.target.value })} />
        </Field>
        <Field label="Warning Threshold (ppm)">
          <input type="number" className="input-field w-full" value={form.warning_threshold} onChange={(e) => setForm({ ...form, warning_threshold: e.target.value })} />
        </Field>
        <Field label="Critical Threshold (ppm)">
          <input type="number" className="input-field w-full" value={form.critical_threshold} onChange={(e) => setForm({ ...form, critical_threshold: e.target.value })} />
        </Field>
        <div className="flex gap-2 pt-2">
          <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
          <button type="submit" className="btn-primary flex-1">Save</button>
        </div>
      </form>
    </div>
  )
}

function Field({ label, children }) {
  return (
    <div>
      <label className="text-[11px] font-mono uppercase tracking-widest text-ink-500 block mb-1">{label}</label>
      {children}
    </div>
  )
}
