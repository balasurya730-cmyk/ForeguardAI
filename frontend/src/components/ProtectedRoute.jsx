import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'

export default function ProtectedRoute({ children, roles }) {
  const { user } = useAuth()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (roles && !roles.includes(user.role)) {
    return (
      <div className="p-8 text-center">
        <p className="text-ink-500">You don't have permission to view this page.</p>
      </div>
    )
  }

  return children
}
