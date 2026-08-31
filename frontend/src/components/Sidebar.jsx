import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Cog,
  HardHat,
  Flame,
  Timer,
  Bell,
  FileImage,
  LineChart,
  FileText,
  Settings,
  ShieldCheck,
  Video
} from 'lucide-react'
import { useAuth } from '../hooks/useAuth.jsx'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/machines', label: 'Machines', icon: Cog },
  { to: '/workers', label: 'Workers', icon: HardHat },
  { to: '/cameras', label: 'Live Cameras', icon: Video },
  { to: '/safety', label: 'Safety Monitoring', icon: ShieldCheck },
  { to: '/gas', label: 'Gas Monitoring', icon: Flame },
  { to: '/runtime', label: 'Runtime Control', icon: Timer },
  { to: '/alerts', label: 'Alerts', icon: Bell },
  { to: '/evidence', label: 'Evidence', icon: FileImage },
  { to: '/analytics', label: 'Analytics', icon: LineChart },
  { to: '/reports', label: 'Reports', icon: FileText },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar({ open, onClose }) {
  const { user } = useAuth()
  
  // Worker (OPERATOR) specific routes
  const workerRoutes = ['/', '/machines', '/gas', '/runtime', '/settings']
  
  // MD (ADMIN) specific routes
  const mdRoutes = ['/cameras', '/safety', '/evidence']
  
  const filteredNavItems = user?.role === 'OPERATOR' 
    ? NAV_ITEMS.filter(item => workerRoutes.includes(item.to))
    : user?.role === 'ADMIN'
    ? NAV_ITEMS.filter(item => mdRoutes.includes(item.to))
    : NAV_ITEMS

  return (
    <>
      {open && (
        <div className="fixed inset-0 bg-black/60 z-30 lg:hidden" onClick={onClose} />
      )}
      <aside
        className={`fixed lg:static z-40 top-0 left-0 h-full w-64 bg-base-900 border-r border-base-600 flex flex-col transition-transform duration-200
        ${open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
      >
        <div className="h-16 flex items-center gap-2.5 px-5 border-b border-base-600">
          <div className="w-8 h-8 rounded-md bg-signal-cyan/15 border border-signal-cyan/40 flex items-center justify-center">
            <ShieldCheck size={18} className="text-signal-cyan" />
          </div>
          <div>
            <div className="font-display font-semibold text-sm tracking-wide text-ink-900">FORGEGUARD</div>
            <div className="text-[10px] font-mono text-ink-500 tracking-widest -mt-0.5">AI PLATFORM</div>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto py-3 px-3 space-y-0.5">
          {filteredNavItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition ${
                  isActive
                    ? 'bg-signal-cyan/10 text-signal-cyan border border-signal-cyan/25'
                    : 'text-ink-500 border border-transparent hover:text-ink-900 hover:bg-base-700'
                }`
              }
            >
              <Icon size={17} strokeWidth={2} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-base-600">
          <div className="text-[10px] font-mono text-ink-500 tracking-widest">SYSTEM MODE</div>
          <div className="mt-1 flex items-center gap-2">
            <span className="live-pulse" />
            <span className="text-xs font-mono text-signal-cyan">DEMO ACTIVE</span>
          </div>
        </div>
      </aside>
    </>
  )
}
