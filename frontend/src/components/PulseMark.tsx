/**
 * Signature element: a live "vital signs" pulse line. The product's core
 * idea is monitoring organizational health and flagging risk before it
 * becomes attrition -- so the brand mark is literally a heartbeat trace,
 * and the same waveform reappears as a subtle ambient motif behind the
 * login card and as a live/loading indicator on KPI cards.
 */
export function PulseMark({ className = "h-7 w-7" }: { className?: string }) {
  return (
    <svg viewBox="0 0 48 48" fill="none" className={className} aria-hidden="true">
      <rect width="48" height="48" rx="12" fill="#7C9EFF" fillOpacity="0.12" />
      <path
        d="M6 24H14L18 12L24 36L28 20L31 24H42"
        stroke="#7C9EFF"
        strokeWidth="2.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function PulseLine({ colorClass = "text-brand", className = "" }: { colorClass?: string; className?: string }) {
  return (
    <svg viewBox="0 0 120 24" className={`${colorClass} ${className}`} fill="none">
      <path
        d="M0 12H24L30 3L38 21L44 12L50 15L54 12H120"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity="0.9"
      />
    </svg>
  );
}
