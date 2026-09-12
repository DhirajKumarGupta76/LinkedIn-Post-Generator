import { useEffect, useMemo, useState } from 'react'
import { Sparkles, LoaderCircle, Copy, Save, RefreshCw, Share2, Pencil, Wand2, Hash, MessageSquareText, ArrowRight } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'
import Input from '../components/Input'
import Button from '../components/Button'
import ShareButtons from '../components/ShareButtons'
import api, { getCurrentUser } from '../services/api'

const achievementOptions = [
  'New Job', 'Internship', 'Promotion', 'Certification', 'Project Completed', 'Hackathon', 'Competition',
  'Academic Achievement', 'Learning Milestone', 'Career Milestone', 'Personal Achievement',
  'Team Achievement', 'Other',
]

const moodOptions = ['Excited', 'Happy', 'Grateful', 'Confident', 'Motivated', 'Inspirational', 'Humble', 'Professional', 'Reflective', 'Proud']
const wordLengthOptions = ['Short', 'Medium', 'Long', 'Custom']
const toneOptions = ['Professional', 'Friendly', 'Inspirational', 'Storytelling', 'Emotional', 'Confident', 'Humble', 'Thought Leadership', 'Casual Professional']
const audienceOptions = ['Recruiters', 'Developers', 'Students', 'Entrepreneurs', 'AI/ML Professionals', 'General LinkedIn Audience', 'Hiring Managers', 'Tech Community']
const styleOptions = ['Storytelling', 'Achievement Announcement', 'Lessons Learned', 'Career Journey', 'Technical Explanation', 'Problem → Solution', 'Before → After', 'Personal Experience', 'Motivational', 'Thought Leadership']

const loadingMessages = [
  'Analyzing your idea...',
  'Choosing the right tone...',
  'Building your story...',
  'Polishing your LinkedIn post...',
]

const initialForm = {
  topic: '',
  achievement: 'Promotion',
  mood: 'Excited',
  feeling: '',
  word_length: 'Medium',
  tone: 'Professional',
  audience: 'Developers',
  style: 'Achievement Announcement',
}

export default function Generator() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [form, setForm] = useState(initialForm)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState('')
  const [posts, setPosts] = useState([])
  const [loadingStage, setLoadingStage] = useState(0)
  const [profile, setProfile] = useState(null)
  const [toast, setToast] = useState('')
  const [hooks, setHooks] = useState([])
  const [hashtags, setHashtags] = useState([])
  const [ctas, setCtas] = useState([])
  const [repurposeText, setRepurposeText] = useState('')
  const [repurposePlatform, setRepurposePlatform] = useState('x')
  const [repurposeResult, setRepurposeResult] = useState('')

  const selectedStyles = useMemo(() => loadingMessages, [])

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await getCurrentUser()
        setProfile(response.data.user || null)
      } catch (error) {
        setProfile(null)
      }
    }
    fetchProfile()
  }, [])

  const handleChange = (event) => {
    const { name, value } = event.target
    setForm((prev) => ({ ...prev, [name]: value }))
    setError('')
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setIsGenerating(true)
    setLoadingStage(0)

    const progressTimer = window.setInterval(() => {
      setLoadingStage((prev) => (prev + 1) % loadingMessages.length)
    }, 1000)

    try {
      const response = await api.post('/posts/generate', {
        ...form,
        personalized_generation: Boolean(profile?.personal_brand_mode),
      })
      const payload = response.data.data
      setPosts((prev) => [{
        id: Date.now(),
        content: payload.content,
        hashtags: payload.hashtags || [],
        word_count: payload.word_count || 0,
      }, ...prev])
      setForm(initialForm)
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to generate your LinkedIn post right now.')
    } finally {
      window.clearInterval(progressTimer)
      setIsGenerating(false)
      setLoadingStage(0)
    }
  }

  const handleCopy = async (content) => {
    try {
      await navigator.clipboard.writeText(content)
      setToast('Post copied successfully!')
      setTimeout(() => setToast(''), 2200)
    } catch (error) {
      setToast('Unable to copy this post.')
      setTimeout(() => setToast(''), 2200)
    }
  }

  const handleGenerateHooks = async () => {
    if (!form.topic) return
    try {
      const response = await api.post('/ai/hooks', { post_id: Date.now(), text: form.topic })
      setHooks(response.data.data?.content ? [response.data.data.content] : [])
    } catch (error) {
      setError('Unable to generate hooks right now.')
    }
  }

  const handleGenerateHashtags = async () => {
    if (!form.topic) return
    try {
      const response = await api.post('/ai/hashtags', { post_id: Date.now(), text: form.topic })
      setHashtags(response.data.data?.content ? response.data.data.content.split(' ') : [])
    } catch (error) {
      setError('Unable to generate hashtags right now.')
    }
  }

  const handleGenerateCtas = async () => {
    try {
      const response = await api.post('/ai/cta', { post_id: Date.now() })
      setCtas(response.data.data?.content ? response.data.data.content.split('\n').filter(Boolean) : [])
    } catch (error) {
      setError('Unable to generate CTAs right now.')
    }
  }

  const handleRepurpose = async () => {
    if (!repurposeText) return
    try {
      const response = await api.post('/ai/repurpose', { content: repurposeText, platform: repurposePlatform })
      setRepurposeResult(response.data.data.content)
    } catch (error) {
      setError('Unable to repurpose this content right now.')
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
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">Generator</p>
              <h1 className="mt-2 text-3xl font-bold text-slate-900">Create a LinkedIn post</h1>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid gap-5 md:grid-cols-2">
                  <Input label="Topic" id="topic" name="topic" value={form.topic} onChange={handleChange} placeholder="What do you want to talk about?" />
                  <label className="block">
                    <span className="mb-2 block text-sm font-medium text-slate-700">Achievement</span>
                    <select name="achievement" value={form.achievement} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200">
                      {achievementOptions.map((option) => (
                        <option key={option} value={option}>{option}</option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-2 block text-sm font-medium text-slate-700">Mood</span>
                    <select name="mood" value={form.mood} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200">
                      {moodOptions.map((option) => (
                        <option key={option} value={option}>{option}</option>
                      ))}
                    </select>
                  </label>
                  <div className="md:col-span-1">
                    <label htmlFor="feeling" className="mb-2 block text-sm font-medium text-slate-700">Feeling</label>
                    <textarea
                      id="feeling"
                      name="feeling"
                      value={form.feeling}
                      onChange={handleChange}
                      placeholder="How are you feeling about this achievement?"
                      rows={4}
                      className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
                    />
                  </div>
                  <label className="block">
                    <span className="mb-2 block text-sm font-medium text-slate-700">Word Length</span>
                    <select name="word_length" value={form.word_length} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200">
                      {wordLengthOptions.map((option) => (
                        <option key={option} value={option}>{option}</option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-2 block text-sm font-medium text-slate-700">Tone</span>
                    <select name="tone" value={form.tone} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200">
                      {toneOptions.map((option) => (
                        <option key={option} value={option}>{option}</option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-2 block text-sm font-medium text-slate-700">Audience</span>
                    <select name="audience" value={form.audience} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200">
                      {audienceOptions.map((option) => (
                        <option key={option} value={option}>{option}</option>
                      ))}
                    </select>
                  </label>
                  <label className="block">
                    <span className="mb-2 block text-sm font-medium text-slate-700">Style</span>
                    <select name="style" value={form.style} onChange={handleChange} className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200">
                      {styleOptions.map((option) => (
                        <option key={option} value={option}>{option}</option>
                      ))}
                    </select>
                  </label>
                </div>

                {error && <p className="text-sm text-rose-600">{error}</p>}
                {toast && <p className="text-sm text-emerald-600">{toast}</p>}

                <div className="flex flex-col gap-3 border-t border-slate-200 pt-6 sm:flex-row sm:justify-between sm:items-center">
                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <Sparkles className="h-4 w-4 text-violet-500" />
                    {isGenerating ? selectedStyles[loadingStage] : 'AI-powered professional writing'}
                  </div>
                  <div className="flex items-center gap-3">
                    <label className="inline-flex items-center gap-2 text-sm text-slate-600">
                      <input type="checkbox" checked={Boolean(profile?.personal_brand_mode)} readOnly className="h-4 w-4 rounded border-slate-300 text-indigo-600" />
                      Personalized Generation
                    </label>
                    <Button type="submit" disabled={isGenerating} className="min-w-[180px] justify-center">
                      {isGenerating ? (
                        <>
                          <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        'Generate Post'
                      )}
                    </Button>
                  </div>
                </div>
              </form>
            </div>

            <div className="mt-8 grid gap-5 lg:grid-cols-2">
              <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-slate-900">AI enhancement tools</h2>
                <div className="mt-4 space-y-4">
                  <div className="flex flex-wrap gap-2">
                    <Button variant="secondary" onClick={handleGenerateHooks} className="gap-2"><Wand2 className="h-4 w-4" />Generate Hook</Button>
                    <Button variant="secondary" onClick={handleGenerateHashtags} className="gap-2"><Hash className="h-4 w-4" />Generate Hashtags</Button>
                    <Button variant="secondary" onClick={handleGenerateCtas} className="gap-2"><MessageSquareText className="h-4 w-4" />Generate CTAs</Button>
                  </div>

                  {hooks.length > 0 && (
                    <div>
                      <p className="mb-2 text-sm font-medium text-slate-700">Hooks</p>
                      <ul className="space-y-2 text-sm text-slate-600">
                        {hooks.map((hook) => (
                          <li key={hook} className="rounded-xl bg-slate-50 p-3">{hook}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {hashtags.length > 0 && (
                    <div>
                      <p className="mb-2 text-sm font-medium text-slate-700">Hashtags</p>
                      <div className="flex flex-wrap gap-2">
                        {hashtags.map((tag) => (
                          <span key={tag} className="rounded-full bg-violet-50 px-2.5 py-1 text-xs font-medium text-violet-700">{tag}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {ctas.length > 0 && (
                    <div>
                      <p className="mb-2 text-sm font-medium text-slate-700">CTAs</p>
                      <ul className="space-y-2 text-sm text-slate-600">
                        {ctas.map((cta) => (
                          <li key={cta} className="rounded-xl bg-slate-50 p-3">{cta}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-slate-900">Repurpose</h2>
                <div className="mt-4 space-y-4">
                  <textarea value={repurposeText} onChange={(event) => setRepurposeText(event.target.value)} rows={5} placeholder="Paste your LinkedIn post to repurpose for another platform" className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200" />
                  <div className="flex gap-3">
                    <select value={repurposePlatform} onChange={(event) => setRepurposePlatform(event.target.value)} className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200">
                      <option value="x">X post</option>
                      <option value="instagram">Instagram caption</option>
                      <option value="facebook">Facebook post</option>
                      <option value="whatsapp">WhatsApp message</option>
                      <option value="email">Email</option>
                    </select>
                    <Button variant="secondary" onClick={handleRepurpose} className="shrink-0"><ArrowRight className="mr-2 h-4 w-4" />Repurpose</Button>
                  </div>

                  {repurposeResult && (
                    <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-700 whitespace-pre-line">{repurposeResult}</div>
                  )}
                </div>
              </div>
            </div>

            {posts.length > 0 && (
              <div className="mt-8 grid gap-5 lg:grid-cols-2">
                {posts.map((post) => (
                  <article key={post.id} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                    <div className="mb-4 flex items-center justify-between text-sm text-slate-500">
                      <span>{post.word_count} words</span>
                      <span>LinkedIn draft</span>
                    </div>
                    <p className="whitespace-pre-line text-[15px] leading-7 text-slate-700">{post.content}</p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {post.hashtags.map((tag) => (
                        <span key={`${post.id}-${tag}`} className="rounded-full bg-violet-50 px-2.5 py-1 text-xs font-medium text-violet-700">{tag}</span>
                      ))}
                    </div>
                    <div className="mt-5 flex flex-wrap gap-2">
                      <Button variant="secondary" className="gap-2" onClick={() => handleCopy(post.content)}>
                        <Copy className="h-4 w-4" />
                        Copy
                      </Button>
                      <Button variant="secondary" className="gap-2">
                        <Pencil className="h-4 w-4" />
                        Edit
                      </Button>
                      <Button variant="secondary" className="gap-2">
                        <Save className="h-4 w-4" />
                        Save
                      </Button>
                      <Button variant="secondary" className="gap-2">
                        <RefreshCw className="h-4 w-4" />
                        Regenerate
                      </Button>
                      <ShareButtons content={post.content} title="LinkedIn Post" onCopy={handleCopy} />
                    </div>
                  </article>
                ))}
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
