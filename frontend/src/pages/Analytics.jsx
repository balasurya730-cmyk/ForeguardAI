import { useEffect, useState } from 'react'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { LoadingState } from '../components/States.jsx'
import { machineService } from '../services/machineService.js'
import { safetyService } from '../services/safetyService.js'
import { alertService } from '../services/alertService.js'

const PIE_COLORS = ['#0ea5e9', '#f59e0b', '#ef4444', '#10b981', '#8b5cf6']

export default function Analytics() {
  const [machines, setMachines] = useState([])
  const [events, setEvents] = useState([])
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([machineService.list(), safetyService.listEvents(500), alertService.list()]).then(
      ([m, e, a]) => {
        setMachines(m)
        setEvents(e)
        setAlerts(a)
        setLoading(false)
      }
    )
  }, [])

  if (loading) return <LoadingState label="Crunching analytics..." />

  const healthData = machines.map((m) => ({ name: m.machine_code, health: m.health_score }))

  const violationCounts = events
    .filter(e => ['NO_HELMET', 'NO_GLOVES', 'NO_BOOTS', 'NO_GLASSES', 'NO_SAFETY_VEST', 'MOBILE_PHONE'].includes(e.violation_type))
    .reduce((acc, e) => {
      const key = e.violation_type.replace('_', ' ')
      acc[key] = (acc[key] || 0) + 1
      return acc
    }, {})
  const violationData = Object.entries(violationCounts).map(([name, value]) => ({ name, value }))

  const alertCounts = alerts.reduce((acc, a) => {
    acc[a.alert_type] = (acc[a.alert_type] || 0) + 1
    return acc
  }, {})
  const alertData = Object.entries(alertCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)
    .map(([name, value]) => ({ name, value }))

  const helmetCompliance = (() => {
    const total = events.filter((e) => e.violation_type === 'NO_HELMET').length
    const compliant = Math.max(0, machines.length * 10 - total) // illustrative baseline for a compliance ratio
    return [
      { name: 'Compliant', value: compliant },
      { name: 'Violations', value: total },
    ]
  })()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink-900">Analytics</h1>
        <p className="text-sm text-ink-500 mt-0.5">Trends across machine health, safety, and alerts</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <ChartCard title="Machine Health Comparison">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={healthData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1D232C" />
              <XAxis dataKey="name" stroke="#7C8797" fontSize={11} />
              <YAxis stroke="#7C8797" fontSize={11} domain={[0, 100]} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="health" fill="#2DD4C8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Safety Violation Breakdown">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={violationData} dataKey="value" nameKey="name" outerRadius={90} label stroke="none">
                {violationData.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Top Alert Types">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={alertData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#1D232C" />
              <XAxis type="number" stroke="#7C8797" fontSize={11} />
              <YAxis type="category" dataKey="name" stroke="#7C8797" fontSize={10} width={140} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="value" fill="#F5A623" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Helmet Compliance (illustrative)">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={helmetCompliance} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} stroke="none">
                <Cell fill="#10B981" />
                <Cell fill="#EF4444" />
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  )
}

const tooltipStyle = { background: '#151A21', border: '1px solid #2A313C', borderRadius: 8, fontSize: 12 }

function ChartCard({ title, children }) {
  return (
    <div className="panel p-4">
      <h3 className="font-display text-sm font-semibold text-ink-900 mb-3">{title}</h3>
      {children}
    </div>
  )
}
