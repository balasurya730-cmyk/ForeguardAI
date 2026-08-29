import { useState, useEffect } from 'react'
import { Play, Square } from 'lucide-react'

function formatHMS(totalSeconds) {
  const h = Math.floor(totalSeconds / 3600)
  const m = Math.floor((totalSeconds % 3600) / 60)
  const s = Math.floor(totalSeconds % 60)
  return [h, m, s].map((v) => String(v).padStart(2, '0')).join(':')
}

export default function RuntimeControl({ machine, runtime, onStart, onStop }) {
  const [hours, setHours] = useState(1)
  const [minutes, setMinutes] = useState(0)
  const [localElapsed, setLocalElapsed] = useState(runtime?.elapsed_seconds ?? 0)

  const isRunning = runtime?.status === 'RUNNING'

  // Smoothly tick the elapsed/remaining display between server updates.
  useEffect(() => {
    setLocalElapsed(runtime?.elapsed_seconds ?? 0)
  }, [runtime?.elapsed_seconds])

  useEffect(() => {
    if (!isRunning) return
    const interval = setInterval(() => setLocalElapsed((v) => v + 1), 1000)
    return () => clearInterval(interval)
  }, [isRunning])

  const configured = runtime?.configured_seconds ?? 0
  const remaining = Math.max(0, configured - localElapsed)

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="font-display font-semibold text-ink-900">{machine.name}</div>
          <div className="text-xs font-mono text-ink-500">{machine.machine_code}</div>
        </div>
        <span
          className={`badge ${isRunning ? 'badge-normal' : 'badge-offline'}`}
        >
          <span className="status-dot bg-current" />
          {runtime?.status || 'STOPPED'}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-5">
        <ReadoutBlock label="Configured" value={formatHMS(configured)} />
        <ReadoutBlock label="Elapsed" value={formatHMS(localElapsed)} tone="amber" />
        <ReadoutBlock label="Remaining" value={formatHMS(remaining)} tone="cyan" />
      </div>

      {!isRunning ? (
        <div className="flex items-end gap-2">
          <div className="flex-1">
            <label className="text-[11px] font-mono uppercase tracking-widest text-ink-500 block mb-1">Hours</label>
            <input
              type="number"
              min={0}
              max={23}
              value={hours}
              onChange={(e) => setHours(Number(e.target.value))}
              className="input-field w-full"
            />
          </div>
          <div className="flex-1">
            <label className="text-[11px] font-mono uppercase tracking-widest text-ink-500 block mb-1">Minutes</label>
            <input
              type="number"
              min={0}
              max={59}
              value={minutes}
              onChange={(e) => setMinutes(Number(e.target.value))}
              className="input-field w-full"
            />
          </div>
          <button
            onClick={() => onStart(hours * 3600 + minutes * 60)}
            className="btn-primary flex items-center gap-2 whitespace-nowrap"
          >
            <Play size={16} /> Start
          </button>
        </div>
      ) : (
        <button onClick={onStop} className="btn-danger w-full flex items-center justify-center gap-2">
          <Square size={16} /> Stop Machine
        </button>
      )}
    </div>
  )
}

function ReadoutBlock({ label, value, tone = 'default' }) {
  const toneClass = tone === 'amber' ? 'text-signal-amber' : tone === 'cyan' ? 'text-signal-cyan' : 'text-ink-900'
  return (
    <div className="bg-base-900 rounded-md border border-base-600 px-2 py-3 text-center">
      <div className="text-[10px] font-mono uppercase tracking-widest text-ink-500 mb-1">{label}</div>
      <div className={`font-mono text-xl font-semibold tabular-nums ${toneClass}`}>{value}</div>
    </div>
  )
}
