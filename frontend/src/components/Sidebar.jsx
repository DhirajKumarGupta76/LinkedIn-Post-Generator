import { BarChart3, FileText, History, Bookmark, UserCircle2, Settings, Sparkles } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { label: 'Dashboard', to: '/dashboard', icon: BarChart3 },
  { label: 'Generate Post', to: '/generate', icon: Sparkles },
  { label: 'History', to: '/history', icon: History },
  { label: 'Saved Posts', to: '/saved', icon: Bookmark },
  { label: 'Profile', to: '/profile', icon: UserCircle2 },
  { label: 'Settings', to: '/settings', icon: Settings },
]

export default function Sidebar({ mobileOpen = false, onClose }) {
  return (
    <>
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-72 border-r border-slate-200 bg-slate-50 p-4 transition-transform duration-200 lg:static lg:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="mb-8 flex items-center gap-3 px-2 pt-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <p className="text-lg font-semibold text-slate-900">PostGen AI</p>
            <p className="text-xs text-slate-500">Creator workspace</p>
          </div>
        </div>

        <nav className="space-y-2">
          {navItems.map(({ label, to, icon: Icon }) => (
            <NavLink
              key={label}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                  isActive
                    ? 'bg-slate-900 text-white shadow-sm'
                    : 'text-slate-600 hover:bg-slate-200 hover:text-slate-900'
                }`
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {mobileOpen && (
        <button
          type="button"
          aria-label="Close sidebar"
          onClick={onClose}
          className="fixed inset-0 z-30 bg-slate-900/30 lg:hidden"
        />
      )}
    </>
  )
}
