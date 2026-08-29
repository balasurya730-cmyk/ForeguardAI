import { Flame } from 'lucide-react'
import StatusBadge from './StatusBadge.jsx'

const STATUS_BAR_COLOR = {
  SAFE: 'bg-signal-cyan',
  WARNING: 'bg-signal-amber',
  CRITICAL: 'bg-signal-red',
}

export default function GasZoneCard({ zone }) {
  const pct = Math.min(100, (zone.current_ppm / zone.critical_threshold) * 100)

  return (
    <div className="panel p-4">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <Flame size={16} className="text-signal-amber" />
          <div>
            <div className="font-display font-semibold text-ink-900">{zone.zone_name}</div>
            <div className="text-xs font-mono text-ink-500">{zone.gas_type}</div>
          </div>
        </div>
        <StatusBadge status={zone.status} />
      </div>

      <div className="flex items-end justify-between mb-1.5">
        <span className="font-mono text-2xl font-semibold text-ink-900">{zone.current_ppm.toFixed(0)}</span>
        <span className="text-xs font-mono text-ink-500 mb-1">ppm</span>
      </div>

      <div className="w-full h-2 bg-base-700 rounded-full overflow-hidden relative">
        <div
          className={`h-full rounded-full transition-all ${STATUS_BAR_COLOR[zone.status]}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="flex justify-between text-[10px] font-mono text-ink-500 mt-1">
        <span>Warn {zone.warning_threshold}</span>
        <span>Crit {zone.critical_threshold}</span>
      </div>
    </div>
  )
}
