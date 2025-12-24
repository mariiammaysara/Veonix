export default function VeonixLogo({ size = 32 }) {
  return (
    <div className="flex items-center gap-2 select-none">
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        fill="none"
      >
        <path
          d="M20 75 L50 20 L80 75"
          stroke="#34d399"
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle
          cx="50"
          cy="55"
          r="6"
          fill="#10b981"
        />
      </svg>

      <span className="font-semibold text-xl tracking-wide text-slate-100">
        Veonix
      </span>
    </div>
  )
}
