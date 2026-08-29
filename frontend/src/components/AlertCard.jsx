import { AlertTriangle, AlertOctagon, Info, Check, CheckCheck } from 'lucide-react'
import StatusBadge from './StatusBadge.jsx'

const SEVERITY_ICON = {
  CRITICAL: AlertOctagon,
  WARNING: AlertTriangle,
  INFO: Info,
}

const SEVERITY_COLOR = {
  CRITICAL: 'text-signal-red',
  WARNING: 'text-signal-amber',
  INFO: 'text-signal-cyan',
}

export default function AlertCard({ alert, onAcknowledge, onResolve }) {
  const Icon = SEVERITY_ICON[alert.severity] || Info

  return (
    <div className="panel p-3.5 flex items-start gap-3">
      <Icon size={18} className={`mt-0.5 shrink-0 ${SEVERITY_COLOR[alert.severity]}`} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-mono text-ink-500">{alert.alert_type}</span>
          <StatusBadge status={alert.status} />
        </div>
        <div className="text-sm text-ink-900 mt-1">{alert.message}</div>
        <div className="text-[11px] font-mono text-ink-500 mt-1">
          {new Date(alert.created_at).toLocaleString()}
        </div>
      </div>
      {alert.status !== 'RESOLVED' && (
        <div className="flex flex-col gap-1.5 shrink-0">
          {alert.status === 'ACTIVE' && (
            <button
              onClick={() => onAcknowledge?.(alert.id)}
              className="p-1.5 rounded-md hover:bg-base-700 text-ink-500 hover:text-signal-amber transition"
              title="Acknowledge"
            >
              <Check size={16} />
            </button>
          )}
          <button
            onClick={() => onResolve?.(alert.id)}
            className="p-1.5 rounded-md hover:bg-base-700 text-ink-500 hover:text-signal-cyan transition"
            title="Resolve"
          >
            <CheckCheck size={16} />
          </button>
        </div>
      )}
    </div>
  )
}
