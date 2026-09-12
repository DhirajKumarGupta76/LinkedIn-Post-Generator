import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'
import PostCard from '../components/PostCard'
import { demoPosts } from '../utils/helpers'

export default function SavedPosts() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1">
          <Navbar />
          <main className="section-shell py-8">
            <div className="mb-8">
              <p className="text-sm font-semibold uppercase tracking-[0.18em] text-indigo-600">Saved Posts</p>
              <h1 className="mt-2 text-3xl font-bold text-slate-900">Your favorite drafts</h1>
            </div>

            {demoPosts.length > 0 ? (
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {demoPosts.map((post) => (
                  <PostCard key={post.title} {...post} />
                ))}
              </div>
            ) : (
              <div className="rounded-3xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-600">
                You have no saved posts yet.
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
