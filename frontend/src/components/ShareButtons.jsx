import { Copy, Globe2, Mail, MessageCircle, Share2 } from 'lucide-react'

const platformStyles = {
  linkedin: 'bg-blue-600 text-white hover:bg-blue-500',
  twitter: 'bg-sky-500 text-white hover:bg-sky-400',
  facebook: 'bg-blue-700 text-white hover:bg-blue-600',
  whatsapp: 'bg-emerald-500 text-white hover:bg-emerald-400',
  email: 'bg-slate-700 text-white hover:bg-slate-600',
  copy: 'bg-white text-slate-900 border border-slate-200 hover:bg-slate-50',
}

export default function ShareButtons({ content, title = 'LinkedIn Post', url = 'https://www.linkedin.com', onCopy }) {
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content || '')
      if (onCopy) onCopy('Post copied successfully!')
      else window.alert('Post copied successfully!')
    } catch (error) {
      if (onCopy) onCopy('Unable to copy this post.')
      else window.alert('Unable to copy this post.')
    }
  }

  const links = [
    {
      key: 'linkedin',
      label: 'LinkedIn',
      href: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
      icon: Share2,
    },
    {
      key: 'twitter',
      label: 'X/Twitter',
      href: `https://twitter.com/intent/tweet?text=${encodeURIComponent(content || title)}`,
      icon: Globe2,
    },
    {
      key: 'facebook',
      label: 'Facebook',
      href: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
      icon: Globe2,
    },
    {
      key: 'whatsapp',
      label: 'WhatsApp',
      href: `https://api.whatsapp.com/send?text=${encodeURIComponent(content || title)}`,
      icon: MessageCircle,
    },
    {
      key: 'email',
      label: 'Email',
      href: `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(content || '')}`,
      icon: Mail,
    },
  ]

  return (
    <div className="flex flex-wrap gap-2">
      {links.map(({ key, label, href, icon: Icon }) => (
        <a
          key={key}
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className={`inline-flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-semibold transition-colors ${platformStyles[key]}`}
        >
          <Icon className="h-3.5 w-3.5" />
          {label}
        </a>
      ))}

      <button
        type="button"
        onClick={handleCopy}
        className={`inline-flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-semibold transition-colors ${platformStyles.copy}`}
      >
        <Copy className="h-3.5 w-3.5" />
        Copy
      </button>
    </div>
  )
}
