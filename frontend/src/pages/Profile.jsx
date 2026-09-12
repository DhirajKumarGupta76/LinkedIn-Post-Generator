import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'
import Button from '../components/Button'

export default function Profile() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1">
          <Navbar />
          <main className="section-shell py-8">
            <div className="mb-8">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">Profile</p>
              <h1 className="mt-2 text-3xl font-bold text-slate-900">Your professional profile</h1>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
                <div>
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-indigo-100 text-xl font-bold text-indigo-700">AD</div>
                </div>
                <div className="flex-1">
                  <h2 className="text-2xl font-semibold text-slate-900">Alex Doe</h2>
                  <p className="text-slate-600">Senior Product Strategist</p>
                </div>
                <Button variant="secondary">Edit profile</Button>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
