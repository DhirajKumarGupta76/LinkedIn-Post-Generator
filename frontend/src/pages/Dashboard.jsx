import { useState } from 'react'
import { Bell, ChevronRight, TrendingUp, Sparkles, FileText, FolderArchive } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'
import PostCard from '../components/PostCard'
import Button from '../components/Button'
import { demoPosts } from '../utils/helpers'

const stats = [
  { label: 'Posts generated', value: '128', icon: FileText },
  { label: 'Saved drafts', value: '42', icon: FolderArchive },
  { label: 'Engagement lift', value: '+24%', icon: TrendingUp },
]

export default function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="flex min-h-screen">
        <Sidebar mobileOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <div className="flex-1">
          <Navbar onMenuClick={() => setSidebarOpen((prev) => !prev)} />

          <main className="section-shell py-8">
            <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">Overview</p>
                <h1 className="mt-2 text-3xl font-bold text-slate-900">Welcome back, Alex</h1>
              </div>
              <button type="button" className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700">
                <Bell className="h-4 w-4" />
                Notifications
              </button>
            </div>

            <div className="grid gap-5 md:grid-cols-3">
              {stats.map(({ label, value, icon: Icon }) => (
                <div key={label} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-slate-500">{label}</p>
                    <div className="rounded-xl bg-indigo-50 p-2 text-indigo-600">
                      <Icon className="h-4 w-4" />
                    </div>
                  </div>
                  <p className="mt-4 text-3xl font-bold text-slate-900">{value}</p>
                </div>
              ))}
            </div>

            <div className="mt-8 grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
              <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-5 flex items-center justify-between gap-4">
                  <div>
                    <h2 className="text-xl font-semibold text-slate-900">Recent posts</h2>
                  </div>
                  <button type="button" className="inline-flex items-center gap-1 text-sm font-medium text-indigo-600">
                    View all
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
                <div className="grid gap-4">
                  {demoPosts.map((post) => (
                    <PostCard key={post.title} {...post} />
                  ))}
                </div>
              </section>

              <aside className="rounded-3xl border border-slate-200 bg-gradient-to-br from-slate-900 to-indigo-900 p-6 text-white shadow-lg">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10 text-indigo-200">
                  <Sparkles className="h-5 w-5" />
                </div>
                <h3 className="text-2xl font-semibold">Generate your next post</h3>
                <p className="mt-3 text-sm leading-6 text-slate-200">
                  Turn your latest achievement into a polished LinkedIn story with AI guidance.
                </p>
                <Button variant="secondary" className="mt-6 w-full justify-center bg-white text-slate-900 hover:bg-slate-100">
                  Start generating
                </Button>
              </aside>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
