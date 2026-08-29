import { useEffect, useState, useCallback } from 'react'
import { Cog, HardHat, HeartPulse, ShieldAlert, Flame } from 'lucide-react'
import StatCard from '../components/StatCard.jsx'
import MachineCard from '../components/MachineCard.jsx'
import GasZoneCard from '../components/GasZoneCard.jsx'
import StatusBadge from '../components/StatusBadge.jsx'
import { LoadingState, EmptyState } from '../components/States.jsx'
import { dashboardService } from '../services/dashboardService.js'
import { machineService } from '../services/machineService.js'
import { gasService } from '../services/gasService.js'
import { useWebSocketContext } from '../hooks/WebSocketContext.jsx'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [machines, setMachines] = useState([])
  const [gasZones, setGasZones] = useState([])
  const [loading, setLoading] = useState(true)
  const { on } = useWebSocketContext()

  const loadAll = useCallback(async () => {
    const [summaryData, machineData, zoneData] = await Promise.all([
      dashboardService.summary(),
      machineService.list(),
      gasService.listZones(),
    ])
    setSummary(summaryData)
    setMachines(machineData)
    setGasZones(zoneData)
    setLoading(false)
  }, [])

  useEffect(() => {
    loadAll()
  }, [loadAll])

  // Live updates: patch individual machines/zones in place, refresh
  // summary counts periodically rather than on every tick to avoid churn.
  useEffect(() => {
    const offMachine = on('machine_update', (data) => {
      setMachines((prev) => prev.map((m) => (m.id === data.id ? { ...m, ...data } : m)))
    })
    const offGas = on('gas_update', (data) => {
      setGasZones((prev) => prev.map((z) => (z.id === data.id ? { ...z, ...data } : z)))
    })
    const offAlert = on('alert', () => {
      dashboardService.summary().then(setSummary)
    })
    const offSafety = on('safety_event', () => {
      dashboardService.summary().then(setSummary)
    })

    const interval = setInterval(() => dashboardService.summary().then(setSummary), 8000)

    return () => {
      offMachine()
      offGas()
      offAlert()
      offSafety()
      clearInterval(interval)
    }
  }, [on])

  if (loading) return <LoadingState label="Loading dashboard..." />

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-900">Command Center</h1>
        <p className="text-sm text-ink-500 mt-0.5">Monitor → Detect → Alert → Evidence → Report → Control</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
        <StatCard
          label="Machines Online"
          value={`${summary.machines_online}/${summary.machines_total}`}
          icon={Cog}
          tone="cyan"
        />
        <StatCard label="Workers Monitored" value={summary.workers_monitored} icon={HardHat} />
        <StatCard
          label="Avg Machine Health"
          value={`${summary.average_machine_health}%`}
          icon={HeartPulse}
          tone={summary.average_machine_health >= 80 ? 'cyan' : 'amber'}
        />
        <StatCard label="Safety Alerts" value={summary.safety_alerts} icon={ShieldAlert} tone={summary.safety_alerts > 0 ? 'amber' : 'default'} />
        <StatCard label="Gas Alerts" value={summary.gas_alerts} icon={Flame} tone={summary.gas_alerts > 0 ? 'red' : 'default'} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-4">
          <SectionHeader title="Machine Health" />
          {machines.length === 0 ? (
            <EmptyState title="No machines configured" description="Add machines to start monitoring." />
          ) : (
            <>
              {machines.filter(m => m.status === 'CRITICAL' || m.status === 'WARNING').length > 0 && (
                <div className="mb-6">
                  <h3 className="text-xs font-mono font-semibold text-signal-red uppercase tracking-widest mb-3 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-signal-red animate-pulse"></span>
                    Attention Required
                  </h3>
                  <div className="grid sm:grid-cols-2 gap-4">
                    {machines.filter(m => m.status === 'CRITICAL' || m.status === 'WARNING').map((m) => (
                      <MachineCard key={m.id} machine={m} />
                    ))}
                  </div>
                </div>
              )}
              
              {machines.filter(m => m.status !== 'CRITICAL' && m.status !== 'WARNING').length > 0 && (
                <div>
                  <h3 className="text-xs font-mono font-semibold text-ink-500 uppercase tracking-widest mb-3">
                    Normal Operation
                  </h3>
                  <div className="grid sm:grid-cols-2 gap-4">
                    {machines.filter(m => m.status !== 'CRITICAL' && m.status !== 'WARNING').map((m) => (
                      <MachineCard key={m.id} machine={m} />
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        <div className="space-y-4">
          <SectionHeader title="Gas Zone Status" />
          <div className="space-y-3">
            {gasZones.map((z) => (
              <GasZoneCard key={z.id} zone={z} />
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-3">
          <SectionHeader title="Recent Alerts" />
          <div className="panel divide-y divide-base-600">
            {summary.recent_alerts.length === 0 ? (
              <div className="p-6 text-center text-sm text-ink-500">No alerts yet.</div>
            ) : (
              summary.recent_alerts.map((a) => (
                <div key={a.id} className="p-3 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-sm text-ink-900 truncate">{a.message}</div>
                    <div className="text-[11px] font-mono text-ink-500">
                      {new Date(a.created_at).toLocaleString()}
                    </div>
                  </div>
                  <StatusBadge status={a.status} />
                </div>
              ))
            )}
          </div>
        </div>

        <div className="space-y-3">
          <SectionHeader title="Recent Safety Violations" />
          <div className="panel divide-y divide-base-600">
            {summary.recent_violations.length === 0 ? (
              <div className="p-6 text-center text-sm text-ink-500">No violations recorded.</div>
            ) : (
              summary.recent_violations.map((v) => (
                <div key={v.id} className="p-3 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="text-sm text-ink-900">
                      {v.violation_type.replace('_', ' ')} {v.worker_id ? `— Worker #${v.worker_id}` : ''}
                    </div>
                    <div className="text-[11px] font-mono text-ink-500">
                      {new Date(v.timestamp).toLocaleString()}
                    </div>
                  </div>
                  <span className="text-xs font-mono text-ink-500">{Math.round(v.confidence * 100)}%</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function SectionHeader({ title }) {
  return <h2 className="font-display font-semibold text-ink-900 text-sm uppercase tracking-wide">{title}</h2>
}
