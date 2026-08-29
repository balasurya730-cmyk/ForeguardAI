export default function StatCard({ label, value, sublabel, icon: Icon, tone = 'default' }) {
  const toneClasses = {
    default: 'text-ink-900',
    cyan: 'text-signal-cyan',
    amber: 'text-signal-amber',
    red: 'text-signal-red',
  }

  return (
    <div className="panel p-4 flex items-start justify-between">
      <div>
        <div className="text-[11px] font-mono uppercase tracking-widest text-ink-500">{label}</div>
        <div className={`text-3xl font-display font-semibold mt-1.5 ${toneClasses[tone]}`}>{value}</div>
        {sublabel && <div className="text-xs text-ink-500 mt-1">{sublabel}</div>}
      </div>
      {Icon && (
        <div className="w-9 h-9 rounded-md bg-base-700 border border-base-500 flex items-center justify-center shrink-0">
          <Icon size={17} className={toneClasses[tone]} />
        </div>
      )}
    </div>
  )
}
