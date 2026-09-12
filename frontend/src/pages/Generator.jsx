import { useState } from 'react'
import { Sparkles, LoaderCircle } from 'lucide-react'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'
import Input from '../components/Input'
import Select from '../components/Select'
import Button from '../components/Button'

const toneOptions = ['Professional', 'Confident', 'Friendly', 'Inspirational', 'Bold']
const audienceOptions = ['Founders', 'Executives', 'Students', 'Recruiters', 'General professionals']
const styleOptions = ['Thought leadership', 'Career story', 'Product update', 'Personal reflection', 'Achievement highlight']
const moodOptions = ['Motivated', 'Reflective', 'Confident', 'Grateful', 'Ambitious']
const lengthOptions = ['300-500 words', '500-700 words', '700-900 words']

export default function Generator() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  const handleSubmit = (event) => {
    event.preventDefault()
    setIsGenerating(true)

    window.setTimeout(() => {
      setIsGenerating(false)
    }, 1800)
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
                  <Input label="Topic" id="topic" placeholder="Example: Product strategy, leadership, growth" />
                  <Input label="Achievement" id="achievement" placeholder="Example: Launching a new internal initiative" />
                  <Input label="Mood" id="mood" placeholder="Example: Motivated" />
                  <Input label="Feeling" id="feeling" placeholder="Example: Proud and energized" />
                  <Select label="Word Length" id="wordLength" options={lengthOptions} placeholder="Select length" />
                  <Select label="Tone" id="tone" options={toneOptions} placeholder="Choose a tone" />
                  <Select label="Audience" id="audience" options={audienceOptions} placeholder="Choose your audience" />
                  <Select label="Post Style" id="postStyle" options={styleOptions} placeholder="Select style" />
                </div>

                <div className="flex flex-col gap-3 border-t border-slate-200 pt-6 sm:flex-row sm:justify-between sm:items-center">
                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <Sparkles className="h-4 w-4 text-violet-500" />
                    AI-powered professional writing soon
                  </div>
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
              </form>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
