import { Inbox, Loader2 } from 'lucide-react'

export function EmptyState({ title = 'Nothing here yet', description }) {
  return (
    <div className="panel p-10 flex flex-col items-center justify-center text-center">
      <Inbox size={28} className="text-ink-500 mb-3" />
      <div className="font-medium text-ink-900">{title}</div>
      {description && <div className="text-sm text-ink-500 mt-1 max-w-sm">{description}</div>}
    </div>
  )
}

export function LoadingState({ label = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center gap-2 py-16 text-ink-500">
      <Loader2 size={18} className="animate-spin" />
      <span className="text-sm font-mono">{label}</span>
    </div>
  )
}

export function ErrorState({ message = 'Something went wrong.' }) {
  return (
    <div className="panel p-6 text-center border-signal-red/30">
      <div className="text-signal-red text-sm font-medium">{message}</div>
    </div>
  )
}
