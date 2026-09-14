import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { CheckCircle2, MailWarning, RefreshCcw } from 'lucide-react'
import Button from '../components/Button'
import { resendVerification, verifyEmail } from '../services/api'

export default function VerifyEmail() {
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState('loading')
  const [message, setMessage] = useState('')
  const [email, setEmail] = useState('')

  useEffect(() => {
    const token = searchParams.get('token')
    if (!token) {
      setStatus('invalid')
      setMessage('The verification link is missing a token.')
      return
    }

    const runVerification = async () => {
      try {
        const response = await verifyEmail(token)
        setStatus('success')
        setMessage(response.data.message || 'Your email has been verified successfully.')
      } catch (error) {
        setStatus('invalid')
        setMessage(error.response?.data?.error?.message || 'This verification link is invalid or expired.')
      }
    }

    runVerification()
  }, [searchParams])

  const handleResend = async () => {
    if (!email) {
      setStatus('invalid')
      setMessage('Please enter the email you registered with.')
      return
    }

    try {
      const response = await resendVerification(email)
      setStatus('success')
      setMessage(response.data.message || 'A new verification email has been sent.')
    } catch (error) {
      setStatus('invalid')
      setMessage(error.response?.data?.error?.message || 'Unable to send a new verification email.')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-10">
      <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-200/50 text-center">
        {status === 'loading' && (
          <>
            <MailWarning className="mx-auto h-12 w-12 text-indigo-600" />
            <h1 className="mt-4 text-2xl font-bold text-slate-900">Verifying your email</h1>
            <p className="mt-3 text-slate-600">Please wait while we confirm your account.</p>
          </>
        )}

        {status === 'success' && (
          <>
            <CheckCircle2 className="mx-auto h-12 w-12 text-emerald-500" />
            <h1 className="mt-4 text-2xl font-bold text-slate-900">Email verified</h1>
            <p className="mt-3 text-slate-600">{message}</p>
            <Link to="/login" className="mt-6 inline-block">
              <Button type="button">Go to login</Button>
            </Link>
          </>
        )}

        {status === 'invalid' && (
          <>
            <MailWarning className="mx-auto h-12 w-12 text-amber-500" />
            <h1 className="mt-4 text-2xl font-bold text-slate-900">Verification issue</h1>
            <p className="mt-3 text-slate-600">{message}</p>

            <div className="mt-5 space-y-3 text-left">
              <label className="block text-sm font-medium text-slate-700">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                className="w-full rounded-xl border border-slate-200 px-3 py-2 text-slate-800 focus:border-indigo-500 focus:outline-none"
              />
              <Button type="button" className="w-full justify-center" onClick={handleResend}>
                <RefreshCcw className="h-4 w-4" />
                Resend verification email
              </Button>
            </div>

            <Link to="/login" className="mt-6 inline-block text-sm font-semibold text-indigo-600">
              Back to login
            </Link>
          </>
        )}
      </div>
    </div>
  )
}
