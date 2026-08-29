import { Link } from 'react-router-dom'
import { HardHat } from 'lucide-react'

export default function WorkerCard({ worker, violationCount = 0 }) {
  return (
    <Link
      to={`/workers/${worker.id}`}
      className="panel p-4 flex items-center gap-3 hover:border-signal-cyan/40 transition"
    >
      <div className="w-10 h-10 rounded-full bg-base-700 border border-base-500 flex items-center justify-center shrink-0">
        <HardHat size={18} className="text-signal-amber" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-medium text-ink-900 truncate">{worker.full_name}</div>
        <div className="text-xs font-mono text-ink-500">
          {worker.worker_code} &middot; {worker.department}
        </div>
      </div>
      {violationCount > 0 && (
        <span className="badge-warning shrink-0">{violationCount} flags</span>
      )}
    </Link>
  )
}
