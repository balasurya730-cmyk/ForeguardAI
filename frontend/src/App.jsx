import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth.jsx'
import { WebSocketProvider } from './hooks/WebSocketContext.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import AppLayout from './components/AppLayout.jsx'

import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Machines from './pages/Machines.jsx'
import MachineDetails from './pages/MachineDetails.jsx'
import Workers from './pages/Workers.jsx'
import WorkerDetails from './pages/WorkerDetails.jsx'
import Safety from './pages/Safety.jsx'
import GasMonitoring from './pages/GasMonitoring.jsx'
import RuntimeControlPage from './pages/RuntimeControlPage.jsx'
import Alerts from './pages/Alerts.jsx'
import Evidence from './pages/Evidence.jsx'
import Analytics from './pages/Analytics.jsx'
import Reports from './pages/Reports.jsx'
import Settings from './pages/Settings.jsx'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          element={
            <ProtectedRoute>
              <WebSocketProvider>
                <AppLayout />
              </WebSocketProvider>
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<Dashboard />} />
          <Route path="/machines" element={<Machines />} />
          <Route path="/machines/:id" element={<MachineDetails />} />
          <Route path="/workers" element={<Workers />} />
          <Route path="/workers/:id" element={<WorkerDetails />} />
          <Route path="/safety" element={<Safety />} />
          <Route path="/gas" element={<GasMonitoring />} />
          <Route path="/runtime" element={<RuntimeControlPage />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/evidence" element={<Evidence />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}
