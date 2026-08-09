import type { LucideIcon } from "lucide-react";

interface KpiCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  trend?: { value: string; positive: boolean };
  accent?: "brand" | "healthy" | "warning" | "risk";
}

const ACCENT_MAP = {
  brand: "text-brand bg-brand/10",
  healthy: "text-pulse-healthy bg-pulse-healthy/10",
  warning: "text-pulse-warning bg-pulse-warning/10",
  risk: "text-pulse-risk bg-pulse-risk/10",
};

export function KpiCard({ label, value, icon: Icon, trend, accent = "brand" }: KpiCardProps) {
  return (
    <div className="glass-card group relative overflow-hidden p-5">
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium uppercase tracking-wide text-ink-secondary">{label}</p>
        <div className={`rounded-lg p-2 ${ACCENT_MAP[accent]}`}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
      <p className="kpi-value mt-3">{value}</p>
      {trend && (
        <p className={`mt-1.5 text-xs font-medium ${trend.positive ? "text-pulse-healthy" : "text-pulse-risk"}`}>
          {trend.value}
        </p>
      )}
    </div>
  );
}
