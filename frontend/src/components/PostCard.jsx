import { ArrowUpRight, Clock3, Sparkles } from 'lucide-react'

export default function PostCard({ title, summary, time, category = 'Achievement' }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md">
      <div className="mb-3 flex items-center justify-between gap-3">
        <span className="inline-flex rounded-full bg-indigo-50 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.08em] text-indigo-700">
          {category}
        </span>
        <span className="inline-flex items-center gap-1 text-xs text-slate-500">
          <Clock3 className="h-3.5 w-3.5" />
          {time}
        </span>
      </div>

      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-600">{summary}</p>

      <div className="mt-5 flex items-center justify-between border-t border-slate-200 pt-4">
        <span className="inline-flex items-center gap-2 text-xs font-medium text-slate-500">
          <Sparkles className="h-3.5 w-3.5 text-violet-500" />
          AI optimized
        </span>
        <button type="button" className="inline-flex items-center gap-2 text-sm font-semibold text-slate-900">
          View post
          <ArrowUpRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
