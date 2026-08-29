import { useState } from 'react'
import { Download, FileText } from 'lucide-react'
import { LoadingState } from '../components/States.jsx'
import { reportService } from '../services/dashboardService.js'

const PERIODS = [
  { key: 'daily', label: 'Daily' },
  { key: 'weekly', label: 'Weekly' },
  { key: 'monthly', label: 'Monthly' },
]

export default function Reports() {
  const [period, setPeriod] = useState('daily')
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)

  async function generate(p) {
    setPeriod(p)
    setLoading(true)
    const data = await reportService[p]()
    setReport(data)
    setLoading(false)
  }

  function download() {
    if (!report) return
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `forgeguard-${period}-report-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink-900">Reports</h1>
          <p className="text-sm text-ink-500 mt-0.5">Generate machine health, safety, and runtime summaries</p>
        </div>
        <div className="flex gap-2">
          {PERIODS.map((p) => (
            <button
              key={p.key}
              onClick={() => generate(p.key)}
              className={`px-3 py-1.5 rounded-md text-xs font-mono transition ${
                period === p.key && report ? 'bg-signal-cyan text-base-950' : 'bg-base-700 text-ink-500 hover:text-ink-900'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <LoadingState label="Generating report..." />
      ) : !report ? (
        <div className="panel p-10 flex flex-col items-center text-center">
          <FileText size={28} className="text-ink-500 mb-3" />
          <div className="text-ink-900 font-medium">Choose a report period above</div>
          <div className="text-sm text-ink-500 mt-1">Reports summarize machine health, safety, gas, and runtime data.</div>
        </div>
      ) : (
        <div className="panel p-6 space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-display font-semibold text-ink-900 capitalize">{report.period} Report</div>
              <div className="text-xs font-mono text-ink-500">Generated {new Date(report.generated_at).toLocaleString()}</div>
            </div>
            <button onClick={download} className="btn-secondary flex items-center gap-2">
              <Download size={15} /> Download JSON
            </button>
          </div>

          <ReportSection title="Machine Health Summary">
            <Stat label="Average Health Score" value={`${report.machine_health_summary.average_health_score}%`} />
            <Stat label="Machines Monitored" value={report.machine_health_summary.machines_monitored} />
            <Stat label="Offline Machines" value={report.machine_health_summary.machines_offline.length || 'None'} />
          </ReportSection>

          <ReportSection title="Safety Violations">
            {Object.keys(report.safety_violations).length === 0 ? (
              <div className="text-sm text-ink-500">No violations in this period.</div>
            ) : (
              Object.entries(report.safety_violations).map(([type, count]) => (
                <Stat key={type} label={type.replace('_', ' ')} value={count} />
              ))
            )}
          </ReportSection>

          <ReportSection title="Gas Incidents">
            <Stat label="Threshold Crossings" value={report.gas_incidents} />
          </ReportSection>

          <ReportSection title="Runtime Statistics">
            <Stat label="Sessions" value={report.runtime_statistics.sessions} />
            <Stat label="Total Runtime" value={`${Math.round(report.runtime_statistics.total_runtime_seconds / 60)} min`} />
          </ReportSection>

          <ReportSection title="Recommended Actions">
            <ul className="list-disc list-inside space-y-1 text-sm text-ink-900">
              {report.recommended_actions.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </ReportSection>
        </div>
      )}
    </div>
  )
}

function ReportSection({ title, children }) {
  return (
    <div className="pt-4 border-t border-base-600 first:pt-0 first:border-0">
      <h3 className="text-xs font-mono uppercase tracking-widest text-ink-500 mb-2">{title}</h3>
      <div className="grid sm:grid-cols-3 gap-2">{children}</div>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="bg-base-900 rounded-md px-3 py-2 border border-base-600">
      <div className="text-[10px] uppercase tracking-wide text-ink-500">{label}</div>
      <div className="text-sm font-mono font-medium text-ink-900">{value}</div>
    </div>
  )
}
