import { Menu, LogOut, Wifi, WifiOff } from 'lucide-react'
import { useAuth } from '../hooks/useAuth.jsx'

export default function Navbar({ onMenuClick, wsConnected }) {
  const { user, logout } = useAuth()

  return (
    <header className="h-16 border-b border-base-600 bg-base-900/70 backdrop-blur-sm flex items-center justify-between px-4 lg:px-6 sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-md hover:bg-base-700 text-ink-500"
        >
          <Menu size={20} />
        </button>
        <div className="hidden sm:flex items-center gap-2 text-xs font-mono">
          {wsConnected ? (
            <span className="flex items-center gap-1.5 text-signal-cyan">
              <Wifi size={13} /> LIVE
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-ink-500">
              <WifiOff size={13} /> RECONNECTING
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-right hidden sm:block">
          <div className="text-sm font-medium text-ink-900">{user?.full_name}</div>
          <div className="text-[11px] font-mono text-ink-500 tracking-wide">{user?.role}</div>
        </div>
        <div className="w-9 h-9 rounded-full bg-base-700 border border-base-500 flex items-center justify-center text-sm font-display font-semibold text-signal-cyan">
          {user?.full_name?.charAt(0) ?? '?'}
        </div>
        <button
          onClick={logout}
          className="p-2 rounded-md hover:bg-base-700 text-ink-500 hover:text-signal-red transition"
          title="Log out"
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  )
}
