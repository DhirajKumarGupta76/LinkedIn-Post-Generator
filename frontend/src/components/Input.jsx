export default function Input({ label, id, type = 'text', placeholder, value, onChange, error, ...props }) {
  return (
    <div className="space-y-2">
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-slate-700">
          {label}
        </label>
      )}
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full rounded-xl border bg-white px-3.5 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200 ${error ? 'border-rose-300' : 'border-slate-200'} ${props.className || ''}`}
        {...props}
      />
      {error && <p className="text-xs text-rose-600">{error}</p>}
    </div>
  )
}
