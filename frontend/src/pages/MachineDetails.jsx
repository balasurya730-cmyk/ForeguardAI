import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Trash2 } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import StatusBadge from '../components/StatusBadge.jsx'
import RuntimeControl from '../components/RuntimeControl.jsx'
import { LoadingState } from '../components/States.jsx'
import { machineService } from '../services/machineService.js'
import { useWebSocketContext } from '../hooks/WebSocketContext.jsx'
import { useAuth } from '../hooks/useAuth.jsx'
import { useNavigate } from 'react-router-dom'

const CHART_COLORS = { temperature: '#F5A623', voltage: '#2DD4C8', current: '#3DDC84', vibration: '#EF4444' }

export default function MachineDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [machine, setMachine] = useState(null)
  const [readings, setReadings] = useState([])
  const [runtime, setRuntime] = useState(null)
  const { on } = useWebSocketContext()
  const { user } = useAuth()
  const canManage = user?.role === 'ADMIN' || user?.role === 'MANAGER'
  const isAdmin = user?.role === 'ADMIN'

  const load = useCallback(async () => {
    const [m, r, rt] = await Promise.all([
      machineService.get(id),
      machineService.readings(id, 50),
      machineService.getRuntime(id),
    ])
    setMachine(m)
    setReadings(r.slice().reverse())
    setRuntime(rt)
  }, [id])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    const offMachine = on('machine_update', (data) => {
      if (String(data.id) === String(id)) setMachine((prev) => ({ ...prev, ...data }))
    })
    const offRuntime = on('runtime_update', (data) => {
      if (String(data.machine_id) === String(id)) setRuntime(data)
    })
    return () => {
      offMachine()
      offRuntime()
    }
  }, [on, id])

  async function handleStart(durationSeconds) {
    const rt = await machineService.startRuntime(id, durationSeconds)
    setRuntime(rt)
  }

  async function handleStop() {
    const rt = await machineService.stopRuntime(id)
    setRuntime(rt)
  }

  async function handleDelete() {
    if (!confirm(`Delete ${machine.name}? This cannot be undone.`)) return
    await machineService.remove(id)
    navigate('/machines')
  }

  if (!machine) return <LoadingState label="Loading machine..." />

  const chartData = readings.map((r) => ({
    time: new Date(r.recorded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    temperature: r.temperature,
    voltage: r.voltage,
    current: r.current,
    vibration: r.vibration,
  }))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/machines" className="p-2 rounded-md hover:bg-base-700 text-ink-500">
            <ArrowLeft size={18} />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-display text-2xl font-semibold text-ink-900">{machine.name}</h1>
              <StatusBadge status={machine.status} />
            </div>
            <p className="text-sm font-mono text-ink-500">{machine.machine_code} &middot; {machine.location}</p>
          </div>
        </div>
        {isAdmin && (
          <button onClick={handleDelete} className="p-2 rounded-md hover:bg-signal-red/10 text-ink-500 hover:text-signal-red transition">
            <Trash2 size={18} />
          </button>
        )}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <ChartPanel title="Temperature History" dataKey="temperature" unit="°C" data={chartData} />
          <div className="grid sm:grid-cols-2 gap-4">
            <ChartPanel title="Voltage / Current" dataKey="voltage" secondKey="current" data={chartData} compact />
            <ChartPanel title="Vibration History" dataKey="vibration" unit="mm/s" data={chartData} compact />
          </div>
        </div>

        <div>
          {canManage ? (
            <RuntimeControl machine={machine} runtime={runtime} onStart={handleStart} onStop={handleStop} />
          ) : (
            <div className="panel p-5 text-sm text-ink-500">Runtime control requires manager or admin access.</div>
          )}
        </div>
      </div>
    </div>
  )
}

function ChartPanel({ title, dataKey, secondKey, unit, data, compact }) {
  return (
    <div className="panel p-4">
      <h3 className="font-display text-sm font-semibold text-ink-900 mb-3">{title}</h3>
      <ResponsiveContainer width="100%" height={compact ? 180 : 240}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1D232C" />
          <XAxis dataKey="time" stroke="#7C8797" fontSize={11} tickLine={false} />
          <YAxis stroke="#7C8797" fontSize={11} tickLine={false} unit={unit} />
          <Tooltip contentStyle={{ background: '#151A21', border: '1px solid #2A313C', borderRadius: 8, fontSize: 12 }} />
          <Line type="monotone" dataKey={dataKey} stroke={CHART_COLORS[dataKey]} strokeWidth={2} dot={false} />
          {secondKey && <Line type="monotone" dataKey={secondKey} stroke={CHART_COLORS[secondKey]} strokeWidth={2} dot={false} />}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
