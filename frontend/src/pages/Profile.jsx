import { useEffect, useMemo, useState } from 'react'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'
import Button from '../components/Button'
import Input from '../components/Input'
import { getCurrentUser, updateCurrentUser } from '../services/api'

const initialProfile = {
  name: '',
  bio: '',
  profession: '',
  industry: '',
  skills: '',
  career_goal: '',
  target_audience: '',
  preferred_tone: '',
  preferred_style: '',
  linkedin_url: '',
  github_url: '',
  portfolio_url: '',
  personal_brand_mode: false,
}

export default function Profile() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [form, setForm] = useState(initialProfile)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await getCurrentUser()
        const user = response.data.user || {}
        setForm({
          ...initialProfile,
          name: user.name || '',
          bio: user.bio || '',
          profession: user.profession || '',
          industry: user.industry || '',
          skills: user.skills || '',
          career_goal: user.career_goal || '',
          target_audience: user.target_audience || '',
          preferred_tone: user.preferred_tone || '',
          preferred_style: user.preferred_style || '',
          linkedin_url: user.linkedin_url || '',
          github_url: user.github_url || '',
          portfolio_url: user.portfolio_url || '',
          personal_brand_mode: Boolean(user.personal_brand_mode),
        })
      } catch (error) {
        setMessage('Unable to load your profile right now.')
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [])

  const completion = useMemo(() => {
    const fields = [
      form.profession,
      form.industry,
      form.skills,
      form.career_goal,
      form.target_audience,
      form.preferred_tone,
      form.preferred_style,
    ]
    const value = fields.filter(Boolean).length
    return Math.round((value / fields.length) * 100)
  }, [form])

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSaving(true)
    setMessage('')

    try {
      const response = await updateCurrentUser({
        name: form.name,
        bio: form.bio,
        profession: form.profession,
        industry: form.industry,
        skills: form.skills,
        career_goal: form.career_goal,
        target_audience: form.target_audience,
        preferred_tone: form.preferred_tone,
        preferred_style: form.preferred_style,
        linkedin_url: form.linkedin_url,
        github_url: form.github_url,
        portfolio_url: form.portfolio_url,
        personal_brand_mode: form.personal_brand_mode,
      })
      setMessage(response.data.success ? 'Profile updated successfully.' : 'Profile update failed.')
    } catch (error) {
      setMessage(error.response?.data?.error?.message || 'Unable to save your profile.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="flex min-h-screen">
        <Sidebar mobileOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <div className="flex-1">
          <Navbar onMenuClick={() => setSidebarOpen((prev) => !prev)} />
          <main className="section-shell py-8">
            <div className="mb-8">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">Profile</p>
              <h1 className="mt-2 text-3xl font-bold text-slate-900">Your professional profile</h1>
            </div>

            <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
              <aside className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-indigo-100 text-xl font-bold text-indigo-700">
                    {form.name ? form.name.slice(0, 2).toUpperCase() : 'ME'}
                  </div>
                  <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                    {completion}% complete
                  </span>
                </div>

                <div className="mt-5">
                  <h2 className="text-2xl font-semibold text-slate-900">{form.name || 'Your Name'}</h2>
                  <p className="mt-1 text-slate-600">{form.profession || 'Add your profession'}</p>
                </div>

                <div className="mt-5">
                  <div className="mb-2 flex items-center justify-between text-sm text-slate-600">
                    <span>Profile completeness</span>
                    <span className="font-medium text-slate-900">{completion}%</span>
                  </div>
                  <div className="h-2.5 w-full rounded-full bg-slate-100">
                    <div className="h-2.5 rounded-full bg-indigo-600" style={{ width: `${completion}%` }} />
                  </div>
                </div>

                <div className="mt-6 space-y-3 text-sm text-slate-600">
                  <p><strong className="text-slate-900">Preferred tone:</strong> {form.preferred_tone || 'Not set'}</p>
                  <p><strong className="text-slate-900">Preferred style:</strong> {form.preferred_style || 'Not set'}</p>
                  <p><strong className="text-slate-900">Target audience:</strong> {form.target_audience || 'Not set'}</p>
                </div>
              </aside>

              <form onSubmit={handleSubmit} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-6 flex items-center justify-between gap-4">
                  <h2 className="text-xl font-semibold text-slate-900">Personal brand details</h2>
                  <label className="inline-flex items-center gap-2 text-sm font-medium text-slate-700">
                    <input type="checkbox" name="personal_brand_mode" checked={form.personal_brand_mode} onChange={handleChange} className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
                    Personal Brand Mode
                  </label>
                </div>

                {message && <p className="mb-4 text-sm text-emerald-600">{message}</p>}

                {loading ? (
                  <p className="text-sm text-slate-500">Loading profile…</p>
                ) : (
                  <div className="grid gap-5 md:grid-cols-2">
                    <Input label="Full name" id="name" name="name" value={form.name} onChange={handleChange} />
                    <Input label="Profession" id="profession" name="profession" value={form.profession} onChange={handleChange} placeholder="Software Engineer" />
                    <Input label="Industry" id="industry" name="industry" value={form.industry} onChange={handleChange} placeholder="Artificial Intelligence" />
                    <Input label="Career goal" id="career_goal" name="career_goal" value={form.career_goal} onChange={handleChange} placeholder="AI/ML Engineer" />
                    <Input label="Target audience" id="target_audience" name="target_audience" value={form.target_audience} onChange={handleChange} placeholder="Developers, founders, hiring managers" />
                    <Input label="Preferred tone" id="preferred_tone" name="preferred_tone" value={form.preferred_tone} onChange={handleChange} placeholder="Professional" />
                    <Input label="Preferred style" id="preferred_style" name="preferred_style" value={form.preferred_style} onChange={handleChange} placeholder="Thought Leadership" />
                    <Input label="LinkedIn URL" id="linkedin_url" name="linkedin_url" value={form.linkedin_url} onChange={handleChange} placeholder="https://linkedin.com/in/yourname" />
                    <Input label="GitHub URL" id="github_url" name="github_url" value={form.github_url} onChange={handleChange} placeholder="https://github.com/yourname" />
                    <Input label="Portfolio URL" id="portfolio_url" name="portfolio_url" value={form.portfolio_url} onChange={handleChange} placeholder="https://yourportfolio.com" />
                    <div className="md:col-span-2">
                      <label htmlFor="skills" className="mb-2 block text-sm font-medium text-slate-700">Skills</label>
                      <textarea id="skills" name="skills" value={form.skills} onChange={handleChange} rows={3} placeholder="Python, React, Machine Learning" className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200" />
                    </div>
                    <div className="md:col-span-2">
                      <label htmlFor="bio" className="mb-2 block text-sm font-medium text-slate-700">Bio</label>
                      <textarea id="bio" name="bio" value={form.bio} onChange={handleChange} rows={3} placeholder="A short bio for your profile" className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200" />
                    </div>
                  </div>
                )}

                <div className="mt-6 flex justify-end">
                  <Button type="submit" disabled={saving}>
                    {saving ? 'Saving...' : 'Save profile'}
                  </Button>
                </div>
              </form>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
