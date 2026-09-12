import { Sparkles, Menu } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import Button from './Button'
import useAuth from '../hooks/useAuth'
import { logoutUser } from '../services/api'

export default function Navbar({ onMenuClick }) {
  const navigate = useNavigate()
  const { isAuthenticated, logout } = useAuth()

  const handleLogout = async () => {
    try {
      await logoutUser()
    } catch (error) {
      // Ignore logout API failures and ensure local state is cleared.
    } finally {
      logout()
      navigate('/login', { replace: true })
    }
  }

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onMenuClick}
            className="rounded-lg p-2 text-slate-600 transition hover:bg-slate-100 lg:hidden"
            aria-label="Toggle menu"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900 text-white">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900">PostGen AI</p>
            </div>
          </div>
        </div>

        <nav className="hidden items-center gap-6 text-sm text-slate-600 md:flex">
          <a href="#features" className="transition hover:text-slate-900">Features</a>
          <a href="#how-it-works" className="transition hover:text-slate-900">How it works</a>
          <a href="#testimonials" className="transition hover:text-slate-900">Testimonials</a>
          <a href="#faq" className="transition hover:text-slate-900">FAQ</a>
        </nav>

        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <Button variant="secondary" className="hidden sm:inline-flex" onClick={handleLogout}>Logout</Button>
          ) : (
            <Button variant="secondary" className="hidden sm:inline-flex" onClick={() => navigate('/login')}>Login</Button>
          )}
          <Button onClick={() => navigate('/generate')}>Generate My Post</Button>
        </div>
      </div>
    </header>
  )
}
