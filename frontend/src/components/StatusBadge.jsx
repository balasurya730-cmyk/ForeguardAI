const STATUS_CLASS = {
  NORMAL: 'badge-normal',
  SAFE: 'badge-normal',
  RUNNING: 'badge-normal',
  ACTIVE: 'badge-warning',
  WARNING: 'badge-critical',
  ACKNOWLEDGED: 'badge-warning',
  CRITICAL: 'badge-critical',
  RESOLVED: 'badge-offline',
  STOPPED: 'badge-offline',
  COMPLETED: 'badge-offline',
  OFFLINE: 'badge-offline',
}

export default function StatusBadge({ status }) {
  const cls = STATUS_CLASS[status] || 'badge-offline'
  return (
    <span className={cls}>
      <span className="status-dot bg-current" />
      {status}
    </span>
  )
}
