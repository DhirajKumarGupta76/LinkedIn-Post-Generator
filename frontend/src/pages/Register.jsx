import { useState } from 'react'
import { ArrowLeft, Eye, EyeOff, Mail } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import Button from '../components/Button'
import Input from '../components/Input'
import useAuth from '../hooks/useAuth'
import { getGoogleLoginUrl, registerUser } from '../services/api'

export default function Register() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    confirm_password: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
    setError('')
  }

  const validateForm = () => {
    if (!form.name.trim() || form.name.trim().length < 2) {
      return 'Name is required and must be at least 2 characters long.'
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailPattern.test(form.email.trim())) {
      return 'Please enter a valid email address.'
    }

    if (form.password.length < 8) {
      return 'Password must be at least 8 characters long.'
    }

    if (!/[A-Z]/.test(form.password) || !/[a-z]/.test(form.password) || !/\d/.test(form.password) || !/[^A-Za-z0-9]/.test(form.password)) {
      return 'Password must include uppercase, lowercase, a number, and a special character.'
    }

    if (form.password !== form.confirm_password) {
      return 'Passwords do not match.'
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
      const response = await registerUser(form)
      const { access_token: accessToken, refresh_token: refreshToken, user } = response.data
      await login(user, accessToken, refreshToken)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to create account. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleGmailLogin = async () => {
    try {
      const response = await getGoogleLoginUrl()
      if (!response?.data?.auth_url) {
        throw new Error('Google login URL missing')
      }

      window.location.href = response.data.auth_url
    } catch (err) {
      setError(err.response?.data?.error?.message || err.message || 'Google login is unavailable right now. Please check the backend OAuth configuration and restart the backend if needed.')
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
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">Join us</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">Create your account</h1>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <Input label="Full name" id="name" name="name" placeholder="Jane Doe" value={form.name} onChange={handleChange} />
          <Input label="Email" id="email" name="email" type="email" placeholder="name@company.com" value={form.email} onChange={handleChange} />
          <div className="relative">
            <Input
              label="Password"
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Create a strong password"
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
          <div className="relative">
            <Input
              label="Confirm password"
              id="confirm_password"
              name="confirm_password"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Confirm your password"
              value={form.confirm_password}
              onChange={handleChange}
            />
            <button
              type="button"
              aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
              className="absolute right-3 top-[44px] text-slate-500"
              onClick={() => setShowConfirmPassword((prev) => !prev)}
            >
              {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {error && <p className="text-sm text-rose-600">{error}</p>}
          <Button type="submit" className="w-full justify-center" disabled={loading}>
            {loading ? 'Creating account...' : 'Create account'}
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
        >
          <Mail className="h-4 w-4" />
          Continue with Gmail
        </Button>

        <p className="mt-6 text-center text-sm text-slate-600">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-indigo-600">Login</Link>
        </p>
      </div>
    </div>
  )
}
