export function Logo() {
  return (
    <div className="flex items-center gap-2">
      <svg
        width="32"
        height="32"
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="text-foreground"
      >
        {/* Camera shutter inspired design with time element */}
        <circle cx="16" cy="16" r="14" stroke="currentColor" strokeWidth="1.5" className="opacity-30" />
        <circle cx="16" cy="16" r="10" stroke="currentColor" strokeWidth="1.5" className="opacity-50" />
        <circle cx="16" cy="16" r="6" stroke="currentColor" strokeWidth="1.5" />
        {/* Shutter blades */}
        <path d="M16 6 L16 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M16 22 L16 26" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M6 16 L10 16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M22 16 L26 16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M9.17 9.17 L11.76 11.76" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M20.24 20.24 L22.83 22.83" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M9.17 22.83 L11.76 20.24" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        <path d="M20.24 11.76 L22.83 9.17" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
      <span className="text-xl font-semibold tracking-tight">Momento</span>
    </div>
  )
}
