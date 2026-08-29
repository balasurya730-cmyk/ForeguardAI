import { useAuth } from '../hooks/useAuth.jsx'

export default function Settings() {
  const { user } = useAuth()

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-900">Settings</h1>
        <p className="text-sm text-ink-500 mt-0.5">Account and system information</p>
      </div>

      <div className="panel p-5 space-y-4">
        <h2 className="text-xs font-mono uppercase tracking-widest text-ink-500">Account</h2>
        <Row label="Name" value={user?.full_name} />
        <Row label="Email" value={user?.email} />
        <Row label="Role" value={user?.role} />
      </div>

      <div className="panel p-5 space-y-4">
        <h2 className="text-xs font-mono uppercase tracking-widest text-ink-500">System</h2>
        <Row label="Mode" value="DEMO (simulated sensors + AI)" />
        <Row label="Backend" value="FastAPI + SQLite (MySQL-ready)" />
        <Row label="Realtime" value="WebSocket /ws/dashboard" />
        <p className="text-xs text-ink-500 pt-2 border-t border-base-600">
          To connect real hardware, set <code className="font-mono text-signal-cyan">SYSTEM_MODE=LIVE</code> in the
          backend's <code className="font-mono text-signal-cyan">.env</code> and configure your MQTT broker and
          camera sources. See the project README for details.
        </p>
      </div>
    </div>
  )
}

function Row({ label, value }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-ink-500">{label}</span>
      <span className="text-ink-900 font-medium">{value}</span>
    </div>
  )
}
