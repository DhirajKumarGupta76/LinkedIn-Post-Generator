import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'
import Button from '../components/Button'

export default function Settings() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1">
          <Navbar />
          <main className="section-shell py-8">
            <div className="mb-8">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">Settings</p>
              <h1 className="mt-2 text-3xl font-bold text-slate-900">Manage your workspace preferences</h1>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="space-y-5">
                <div>
                  <h2 className="text-lg font-semibold text-slate-900">Brand voice</h2>
                  <p className="mt-1 text-sm text-slate-600">Define how your generated LinkedIn posts should sound.</p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                  Current setting: Professional, confident, and concise.
                </div>
                <Button variant="secondary">Update preferences</Button>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
