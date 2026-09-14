import { useEffect, useState } from 'react'
import { ArrowLeft, Eye, EyeOff, Mail } from 'lucide-react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import Button from '../components/Button'
import Input from '../components/Input'
import useAuth from '../hooks/useAuth'
import { getGoogleLoginUrl, getCurrentUser, loginUser, refreshSession, setAccessToken } from '../services/api'

export default function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isAuthenticated, loading: authLoading } = useAuth()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
    setError('')
  }

  const validateForm = () => {
    if (!form.email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
      return 'Please enter a valid email address.'
    }

    if (!form.password) {
      return 'Password is required.'
    }

    return ''
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      setLoading(false)
      return
    }

    try {
      const response = await loginUser(form)
      const { access_token: accessToken, user } = response.data
      await login(user, accessToken)
      const redirectPath = location.state?.from?.pathname || '/dashboard'
      navigate(redirectPath, { replace: true })
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to login. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      const params = new URLSearchParams(location.search)
      if (params.get('google') !== 'success') {
        navigate('/dashboard', { replace: true })
      }
    }
  }, [authLoading, isAuthenticated, location.search, navigate])

  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const googleStatus = params.get('google')

    if (googleStatus === 'error') {
      const googleMessage = params.get('message') || 'Google sign-in was denied.'
      setError(decodeURIComponent(googleMessage))
      return
    }

    if (googleStatus !== 'success') {
      return
    }

    let cancelled = false

    const finalizeGoogleLogin = async () => {
      setGoogleLoading(true)
      setError('')
      try {
        const response = await refreshSession()
        const accessToken = response.data?.access_token
        if (!accessToken) {
          throw new Error('Google sign-in did not return an access token.')
        }

        setAccessToken(accessToken)
        const userResponse = await getCurrentUser()
        if (cancelled) {
          return
        }
        await login(userResponse.data.user, accessToken)
        navigate('/dashboard', { replace: true })
      } catch (err) {
        if (!cancelled) {
          const message = err.response?.data?.error?.message || err.message || 'Google sign-in could not be completed.'
          setError(message)
        }
      } finally {
        if (!cancelled) {
          setGoogleLoading(false)
        }
      }
    }

    finalizeGoogleLogin()
    return () => {
      cancelled = true
    }
  }, [location.search, login, navigate])

  const handleGmailLogin = async () => {
    try {
      const response = await getGoogleLoginUrl()
      if (!response?.data?.auth_url) {
        throw new Error('Google login URL missing')
      }

      window.location.href = response.data.auth_url
    } catch (err) {
      setError('Google login is unavailable right now. Please check the backend OAuth configuration and restart the backend if needed.')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
      <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-200/50">
        <Link to="/" className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-slate-600">
          <ArrowLeft className="h-4 w-4" />
          Back to home
        </Link>
        <div className="mb-6">
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">Welcome back</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">Login to PostGen AI</h1>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <Input label="Email" id="email" name="email" type="email" placeholder="name@company.com" value={form.email} onChange={handleChange} />
          <div className="relative">
            <Input
              label="Password"
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••"
              value={form.password}
              onChange={handleChange}
            />
            <button
              type="button"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              className="absolute right-3 top-[44px] text-slate-500"
              onClick={() => setShowPassword((prev) => !prev)}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {error && <p className="text-sm text-rose-600">{error}</p>}
          {googleLoading && <p className="text-sm text-slate-600">Completing Google sign-in...</p>}
          <Button type="submit" className="w-full justify-center" disabled={loading || googleLoading}>
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>

        <div className="mt-6 flex items-center gap-3 text-xs uppercase tracking-[0.18em] text-slate-400">
          <div className="h-px flex-1 bg-slate-200" />
          <span>or</span>
          <div className="h-px flex-1 bg-slate-200" />
        </div>

        <Button
          type="button"
          variant="secondary"
          className="mt-4 w-full justify-center gap-2"
          onClick={handleGmailLogin}
          disabled={googleLoading}
        >
          <Mail className="h-4 w-4" />
          Continue with Gmail
        </Button>

        <p className="mt-6 text-center text-sm text-slate-600">
          Don’t have an account?{' '}
          <Link to="/register" className="font-semibold text-indigo-600">Create one</Link>
        </p>
      </div>
    </div>
  )
}
