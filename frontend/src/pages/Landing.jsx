import { ArrowRight, CheckCircle2, Sparkles, BrainCircuit, MessageSquareQuote, ShieldCheck, ChevronDown, Star } from 'lucide-react'
import Button from '../components/Button'
import Navbar from '../components/Navbar'

const features = [
  { title: 'AI-powered drafts', description: 'Turn your achievements and ideas into polished, high-converting LinkedIn content.', icon: BrainCircuit },
  { title: 'Professional tone', description: 'Shape your voice with personal, confident, leadership-driven messaging.', icon: MessageSquareQuote },
  { title: 'Trust-first workflow', description: 'Stay credible with refined prompts, editing steps, and polished final outputs.', icon: ShieldCheck },
]

const steps = [
  'Add your topic, win, and audience context',
  'Choose tone, length, and post style',
  'Generate a polished post ready for publishing',
]

const capabilities = ['Executive storytelling', 'Achievement framing', 'Thought leadership', 'Audience-specific positioning', 'Brand-ready updates', 'Performance-focused copy']

const testimonials = [
  { quote: 'The drafts feel like a senior strategist wrote them. It helps me turn wins into stories that actually connect.', name: 'Aisha Khan', role: 'Product Lead' },
  { quote: 'I use it to turn my weekly updates into thought leadership posts without spending hours rewriting.', name: 'Marcus Lee', role: 'Founder' },
  { quote: 'The output is clear, professional, and credible. It gives my personal brand a stronger voice.', name: 'Priya Sharma', role: 'Marketing Director' },
]

const faqs = [
  { question: 'Who is PostGen AI for?', answer: 'It is built for founders, professionals, marketers, and teams who want concise, polished LinkedIn updates.' },
  { question: 'Can I tune the tone and audience?', answer: 'Yes—this step focuses on the interface and reusable input patterns so those controls are ready for the AI layer.' },
  { question: 'Is this only for LinkedIn?', answer: 'The current product is designed around LinkedIn content generation, but the architecture is scalable for more formats later.' },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />

      <main>
        <section className="section-shell relative overflow-hidden py-16 sm:py-20 lg:py-24">
          <div className="absolute inset-x-0 top-0 -z-10 h-64 bg-gradient-to-b from-indigo-100 via-white to-transparent" />
          <div className="grid items-center gap-10 lg:grid-cols-[1.2fr_0.8fr]">
            <div>
              <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-indigo-700">
                <Sparkles className="h-3.5 w-3.5" />
                AI content for ambitious professionals
              </div>
              <h1 className="max-w-xl text-4xl font-bold tracking-tight text-slate-950 sm:text-5xl lg:text-6xl">
                Turn Your Achievements Into Powerful LinkedIn Posts
              </h1>
              <p className="mt-6 max-w-xl text-lg text-slate-600">
                Transform your ideas, achievements and feelings into engaging professional LinkedIn content with AI.
              </p>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Button className="rounded-xl px-6 py-3 text-base">Generate My Post <ArrowRight className="ml-2 h-4 w-4" /></Button>
                <Button variant="secondary" className="rounded-xl px-6 py-3 text-base">Try Demo</Button>
              </div>

              <div className="mt-8 flex flex-wrap items-center gap-6 text-sm text-slate-600">
                <div className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-500" /> No credit card required</div>
                <div className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-500" /> Built for professionals</div>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-xl shadow-indigo-100/50">
              <div className="rounded-2xl bg-slate-900 p-5 text-white">
                <div className="mb-6 flex items-center justify-between text-sm text-slate-300">
                  <span>AI Content Overview</span>
                  <span className="rounded-full bg-emerald-500/20 px-2 py-1 text-emerald-300">Live</span>
                </div>
                <div className="space-y-4">
                  <div className="rounded-xl bg-slate-800 p-4">
                    <p className="text-xs uppercase tracking-[0.12em] text-slate-400">Topic</p>
                    <p className="mt-2 text-base font-medium">Product launch strategy</p>
                  </div>
                  <div className="rounded-xl bg-slate-800 p-4">
                    <p className="text-xs uppercase tracking-[0.12em] text-slate-400">Tone</p>
                    <p className="mt-2 text-base font-medium">Confident • Professional • Human</p>
                  </div>
                  <div className="rounded-xl bg-slate-800 p-4">
                    <p className="text-xs uppercase tracking-[0.12em] text-slate-400">Audience</p>
                    <p className="mt-2 text-base font-medium">Founders, operators, and product leaders</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="section-shell py-16 sm:py-20">
          <div className="mb-10 text-center">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">Features</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Designed to turn your momentum into meaningful content</h2>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            {features.map(({ title, description, icon: Icon }) => (
              <div key={title} className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 text-indigo-700">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900">{title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="how-it-works" className="bg-white py-16 sm:py-20">
          <div className="section-shell">
            <div className="mb-10 text-center">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">How It Works</p>
              <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Publish with clarity in three simple steps</h2>
            </div>
            <div className="grid gap-6 md:grid-cols-3">
              {steps.map((step, index) => (
                <div key={step} className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
                  <div className="mb-5 flex h-10 w-10 items-center justify-center rounded-full bg-slate-900 text-sm font-semibold text-white">0{index + 1}</div>
                  <p className="text-base leading-7 text-slate-700">{step}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="section-shell py-16 sm:py-20">
          <div className="mb-10 text-center">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">AI Capabilities</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Built to sound strategic, timely, and authentic</h2>
          </div>
          <div className="flex flex-wrap gap-3 justify-center">
            {capabilities.map((item) => (
              <div key={item} className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm">
                {item}
              </div>
            ))}
          </div>
        </section>

        <section id="testimonials" className="bg-white py-16 sm:py-20">
          <div className="section-shell">
            <div className="mb-10 text-center">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">Testimonials</p>
              <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Professionals are using PostGen AI to tell stronger stories</h2>
            </div>
            <div className="grid gap-6 lg:grid-cols-3">
              {testimonials.map(({ quote, name, role }) => (
                <div key={name} className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
                  <div className="mb-4 flex items-center gap-1 text-amber-400">
                    {[...Array(5)].map((_, idx) => <Star key={idx} className="h-4 w-4 fill-current" />)}
                  </div>
                  <p className="text-base leading-7 text-slate-700">“{quote}”</p>
                  <div className="mt-6 border-t border-slate-200 pt-4">
                    <p className="font-semibold text-slate-900">{name}</p>
                    <p className="text-sm text-slate-500">{role}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="faq" className="section-shell py-16 sm:py-20">
          <div className="mb-10 text-center">
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">FAQ</p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">Questions people ask before they start</h2>
          </div>
          <div className="mx-auto max-w-3xl space-y-4">
            {faqs.map(({ question, answer }) => (
              <div key={question} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex items-center justify-between gap-4">
                  <h3 className="text-base font-semibold text-slate-900">{question}</h3>
                  <ChevronDown className="h-4 w-4 text-slate-500" />
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-600">{answer}</p>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 bg-slate-900 py-10 text-slate-300">
        <div className="section-shell flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-lg font-semibold text-white">PostGen AI</p>
            <p className="mt-1 text-sm">Turn your work into content people remember.</p>
          </div>
          <div className="flex gap-6 text-sm">
            <a href="#features" className="hover:text-white">Features</a>
            <a href="#how-it-works" className="hover:text-white">How it works</a>
            <a href="#faq" className="hover:text-white">FAQ</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
