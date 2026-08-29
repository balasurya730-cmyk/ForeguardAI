import { Link } from 'react-router-dom'
import { Thermometer, Zap, Activity, Waves } from 'lucide-react'
import StatusBadge from './StatusBadge.jsx'

export default function MachineCard({ machine }) {
  const healthColor =
    machine.health_score >= 85 ? 'text-signal-cyan' : machine.health_score >= 60 ? 'text-signal-amber' : 'text-signal-red'

  const borderClass = machine.status === 'CRITICAL' ? 'border-signal-red/50 shadow-[0_0_15px_rgba(244,63,94,0.15)]' :
                      machine.status === 'WARNING' ? 'border-signal-red/50 shadow-[0_0_15px_rgba(244,63,94,0.15)]' : // WARNING uses red mapping now
                      'hover:border-signal-cyan/40'

  return (
    <Link
      to={`/machines/${machine.id}`}
      className={`panel p-4 block transition group ${borderClass}`}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="font-display font-semibold text-ink-900">{machine.name}</div>
          <div className="text-xs font-mono text-ink-500">{machine.machine_code} &middot; {machine.location}</div>
        </div>
        <StatusBadge status={machine.status} />
      </div>

      <div className="grid grid-cols-4 gap-2 mb-3">
        <Metric icon={Thermometer} value={`${machine.temperature.toFixed(1)}°C`} label="Temp" />
        <Metric icon={Zap} value={`${machine.voltage.toFixed(0)}V`} label="Volt" />
        <Metric icon={Activity} value={`${machine.current.toFixed(1)}A`} label="Curr" />
        <Metric icon={Waves} value={`${machine.vibration.toFixed(1)}`} label="Vib" />
      </div>

      <div className="flex items-center justify-between">
        <span className="text-[11px] font-mono uppercase tracking-widest text-ink-500">Health Score</span>
        <span className={`font-mono font-semibold text-lg ${healthColor}`}>{machine.health_score.toFixed(0)}%</span>
      </div>
      <div className="w-full h-1.5 bg-base-700 rounded-full mt-1.5 overflow-hidden">
        <div
          className={`h-full rounded-full ${
            machine.health_score >= 85 ? 'bg-signal-cyan' : machine.health_score >= 60 ? 'bg-signal-amber' : 'bg-signal-red'
          }`}
          style={{ width: `${machine.health_score}%` }}
        />
      </div>
    </Link>
  )
}

function Metric({ icon: Icon, value, label }) {
  return (
    <div className="bg-base-900/60 rounded-md px-2 py-1.5 text-center">
      <Icon size={13} className="text-ink-500 mx-auto mb-1" />
      <div className="text-xs font-mono font-medium text-ink-900">{value}</div>
      <div className="text-[9px] text-ink-500 uppercase tracking-wide">{label}</div>
    </div>
  )
}
