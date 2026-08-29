import { createContext, useContext, useState, useCallback } from 'react'
import { authService } from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(authService.getCurrentUser())

  const login = useCallback(async (email, password) => {
    const loggedInUser = await authService.login(email, password)
    setUser(loggedInUser)
    return loggedInUser
  }, [])

  const register = useCallback(async (fullName, email, password, role) => {
    const registeredUser = await authService.register(fullName, email, password, role)
    setUser(registeredUser)
    return registeredUser
  }, [])

  const logout = useCallback(() => {
    authService.logout()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
