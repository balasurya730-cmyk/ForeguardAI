import { useState } from 'react'
import { useNavigate, Navigate } from 'react-router-dom'
import { ShieldCheck, LogIn, UserPlus, Mail, Eye, EyeOff, ArrowLeft } from 'lucide-react'
import { useAuth } from '../hooks/useAuth.jsx'

export default function Login() {
  const { user, login, register } = useAuth()
  const navigate = useNavigate()
  
  // 'LOGIN' | 'REGISTER' | 'FORGOT_PASSWORD'
  const [view, setView] = useState('LOGIN')
  
  const [email, setEmail] = useState('admin@forgeguard.ai')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [loading, setLoading] = useState(false)

  if (user) return <Navigate to="/" replace />

  function switchView(newView) {
    setView(newView)
    setError('')
    setSuccessMsg('')
    if (newView === 'LOGIN') {
      setEmail('admin@forgeguard.ai')
      setPassword('')
    } else {
      setEmail('')
      setPassword('')
      setFullName('')
    }
  }

  async function handleLogin(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  async function handleRegister(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      // Default to WORKER role for self-registration, or pass expected string
      await register(fullName, email, password, 'worker')
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  function handleForgotPassword(e) {
    e.preventDefault()
    setError('')
    setSuccessMsg('')
    
    // Mock the forgot password flow since SMTP is not configured on the backend
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      setSuccessMsg(`If an account exists for ${email}, a password reset link has been sent.`)
      setEmail('')
    }, 1500)
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-xl bg-signal-cyan/15 border border-signal-cyan/40 flex items-center justify-center mb-4">
            <ShieldCheck size={28} className="text-signal-cyan" />
          </div>
          <h1 className="font-display font-semibold text-xl text-ink-900">FORGEGUARD AI</h1>
          <p className="text-xs font-mono text-ink-500 tracking-wide mt-1">SMART FACTORY COMMAND CENTER</p>
        </div>

        {view === 'LOGIN' && (
          <form onSubmit={handleLogin} className="panel p-6 space-y-4">
            <div>
              <label className="text-xs font-mono uppercase tracking-widest text-ink-500 block mb-1.5">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field w-full"
                placeholder="you@forgeguard.ai"
              />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-mono uppercase tracking-widest text-ink-500 block">Password</label>
                <button 
                  type="button" 
                  onClick={() => switchView('FORGOT_PASSWORD')} 
                  className="text-[11px] font-mono text-signal-cyan hover:underline"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field w-full pr-10"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-ink-500 hover:text-ink-900"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && <div className="text-signal-red text-sm">{error}</div>}

            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
              <LogIn size={16} />
              {loading ? 'Signing in...' : 'Sign in'}
            </button>

            <div className="pt-4 border-t border-base-600 text-center">
              <p className="text-xs text-ink-500">
                Don't have an account?{' '}
                <button 
                  type="button" 
                  onClick={() => switchView('REGISTER')} 
                  className="text-signal-cyan hover:underline font-medium"
                >
                  Create one
                </button>
              </p>
              <div className="text-[11px] font-mono text-ink-500 text-center mt-3">
                Seed logins: admin@forgeguard.ai / Admin@123
              </div>
            </div>
          </form>
        )}

        {view === 'REGISTER' && (
          <form onSubmit={handleRegister} className="panel p-6 space-y-4">
            <div>
              <label className="text-xs font-mono uppercase tracking-widest text-ink-500 block mb-1.5">Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="input-field w-full"
                placeholder="Jane Doe"
              />
            </div>
            <div>
              <label className="text-xs font-mono uppercase tracking-widest text-ink-500 block mb-1.5">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field w-full"
                placeholder="you@forgeguard.ai"
              />
            </div>
            <div>
              <label className="text-xs font-mono uppercase tracking-widest text-ink-500 block mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field w-full pr-10"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-ink-500 hover:text-ink-900"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && <div className="text-signal-red text-sm">{error}</div>}

            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
              <UserPlus size={16} />
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>

            <div className="pt-4 border-t border-base-600 text-center">
              <p className="text-xs text-ink-500">
                Already have an account?{' '}
                <button 
                  type="button" 
                  onClick={() => switchView('LOGIN')} 
                  className="text-signal-cyan hover:underline font-medium"
                >
                  Sign in
                </button>
              </p>
            </div>
          </form>
        )}

        {view === 'FORGOT_PASSWORD' && (
          <form onSubmit={handleForgotPassword} className="panel p-6 space-y-4">
            <h2 className="text-sm font-semibold text-ink-900 mb-2">Reset Password</h2>
            <p className="text-xs text-ink-500 mb-4">
              Enter your email address and we'll send you a link to reset your password.
            </p>

            <div>
              <label className="text-xs font-mono uppercase tracking-widest text-ink-500 block mb-1.5">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field w-full"
                placeholder="you@forgeguard.ai"
              />
            </div>

            {error && <div className="text-signal-red text-sm">{error}</div>}
            {successMsg && <div className="text-signal-cyan text-sm p-3 bg-signal-cyan/10 rounded border border-signal-cyan/20">{successMsg}</div>}

            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
              <Mail size={16} />
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>

            <div className="pt-4 border-t border-base-600 text-center">
              <button 
                type="button" 
                onClick={() => switchView('LOGIN')} 
                className="text-xs text-ink-500 hover:text-ink-900 flex items-center justify-center gap-1 w-full"
              >
                <ArrowLeft size={14} /> Back to login
              </button>
            </div>
          </form>
        )}

      </div>
    </div>
  )
}
