import { useEffect, useState, useCallback } from 'react'
import { Plus, X } from 'lucide-react'
import MachineCard from '../components/MachineCard.jsx'
import { LoadingState, EmptyState } from '../components/States.jsx'
import { machineService } from '../services/machineService.js'
import { useWebSocketContext } from '../hooks/WebSocketContext.jsx'
import { useAuth } from '../hooks/useAuth.jsx'

export default function Machines() {
  const [machines, setMachines] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const { on } = useWebSocketContext()
  const { user } = useAuth()
  const canManage = user?.role === 'ADMIN' || user?.role === 'MANAGER'

  const load = useCallback(async () => {
    const data = await machineService.list()
    setMachines(data)
    setLoading(false)
  }, [])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    return on('machine_update', (data) => {
      setMachines((prev) => prev.map((m) => (m.id === data.id ? { ...m, ...data } : m)))
    })
  }, [on])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900">Machines</h1>
          <p className="text-sm text-ink-500 mt-0.5">{machines.length} machines registered</p>
        </div>
        {canManage && (
          <button onClick={() => setShowForm((v) => !v)} className="btn-primary flex items-center gap-2">
            {showForm ? <X size={16} /> : <Plus size={16} />}
            {showForm ? 'Cancel' : 'Add Machine'}
          </button>
        )}
      </div>

      {showForm && <MachineForm onCreated={() => { setShowForm(false); load() }} />}

      {loading ? (
        <LoadingState label="Loading machines..." />
      ) : machines.length === 0 ? (
        <EmptyState title="No machines yet" description="Add your first machine to begin monitoring." />
      ) : (
        <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {machines.map((m) => (
            <MachineCard key={m.id} machine={m} />
          ))}
        </div>
      )}
    </div>
  )
}

function MachineForm({ onCreated }) {
  const [form, setForm] = useState({ machine_code: '', name: '', location: '' })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      await machineService.create(form)
      onCreated()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not create machine.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="panel p-4 grid sm:grid-cols-4 gap-3 items-end">
      <div>
        <label className="text-[11px] font-mono uppercase tracking-widest text-ink-500 block mb-1">Machine Code</label>
        <input required className="input-field w-full" value={form.machine_code}
          onChange={(e) => setForm({ ...form, machine_code: e.target.value })} placeholder="MOTOR-03" />
      </div>
      <div>
        <label className="text-[11px] font-mono uppercase tracking-widest text-ink-500 block mb-1">Name</label>
        <input required className="input-field w-full" value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Induction Motor 03" />
      </div>
      <div>
        <label className="text-[11px] font-mono uppercase tracking-widest text-ink-500 block mb-1">Location</label>
        <input className="input-field w-full" value={form.location}
          onChange={(e) => setForm({ ...form, location: e.target.value })} placeholder="Bay A" />
      </div>
      <button type="submit" disabled={saving} className="btn-primary">
        {saving ? 'Saving...' : 'Create Machine'}
      </button>
      {error && <div className="text-signal-red text-sm sm:col-span-4">{error}</div>}
    </form>
  )
}
