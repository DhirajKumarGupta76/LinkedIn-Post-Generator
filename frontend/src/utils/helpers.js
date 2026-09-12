export const formatNumber = (value) => new Intl.NumberFormat('en-US').format(value)

export const cn = (...classes) => classes.filter(Boolean).join(' ')

export const demoPosts = [
  {
    title: 'Launching a new chapter in product strategy',
    summary: 'A behind-the-scenes look at how I translated market insights into a clearer product vision for my team.',
    time: '2h ago',
    category: 'Achievement',
  },
  {
    title: 'Celebrating the milestones that shaped our growth',
    summary: 'Reflecting on the habits, feedback, and hard work that pushed our team toward measurable execution.',
    time: 'Yesterday',
    category: 'Reflection',
  },
  {
    title: 'A reminder to trust the process',
    summary: 'What I learned from a season of uncertainty and why consistency ultimately matters more than speed.',
    time: '3 days ago',
    category: 'Mindset',
  },
]
