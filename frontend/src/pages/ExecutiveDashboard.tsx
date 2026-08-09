import { useEffect, useState } from "react";
import {
  Users, UserCheck, TrendingDown, Wallet, Star, Heart, CalendarCheck, Briefcase,
} from "lucide-react";
import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  BarChart, Bar, PieChart, Pie, Cell,
} from "recharts";
import { dashboardApi } from "../api/client";
import type { ExecutiveDashboardResponse } from "../types";
import { KpiCard } from "../components/KpiCard";
import { PageHeader } from "../components/PageHeader";
import { LoadingState, ErrorState } from "../components/StateViews";

const PIE_COLORS = ["#7C9EFF", "#6EE7C9", "#FBBF24", "#FB7185", "#A78BFA", "#38BDF8", "#F472B6", "#34D399"];

export function ExecutiveDashboard() {
  const [data, setData] = useState<ExecutiveDashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    dashboardApi
      .executive()
      .then(setData)
      .catch(() => setError("Could not load executive dashboard data."));
  }, []);

  if (error) return <div className="p-8"><ErrorState message={error} /></div>;
  if (!data) return <LoadingState />;

  const { kpis } = data;
  const isFullAccess = data.access_level === "full";

  return (
    <div className="p-8">
      <PageHeader
        title={isFullAccess ? "Executive Dashboard" : "My Dashboard"}
        subtitle={
          isFullAccess
            ? `Organization-wide workforce KPIs · updated ${data.generated_at}`
            : `Operational overview for your role · updated ${data.generated_at}`
        }
      />

      {!isFullAccess && (
        <div className="mb-4 glass-card border border-brand-500/30 bg-brand-500/5 p-3 text-xs text-ink-secondary">
          Pay, spend, and org-wide attrition figures are limited to manager and HR roles. You're seeing the operational subset for your role.
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-5">
        <KpiCard label="Total Employees" value={kpis.total_employees.toLocaleString()} icon={Users} accent="brand" />
        <KpiCard label="Active Employees" value={kpis.active_employees.toLocaleString()} icon={UserCheck} accent="healthy" />
        {kpis.attrition_rate_pct !== undefined && (
          <KpiCard
            label="Attrition Rate"
            value={`${kpis.attrition_rate_pct}%`}
            icon={TrendingDown}
            accent={kpis.attrition_rate_pct > 20 ? "risk" : "warning"}
          />
        )}
        {kpis.avg_monthly_salary !== undefined && (
          <KpiCard label="Avg. Monthly Salary" value={`$${kpis.avg_monthly_salary.toLocaleString()}`} icon={Wallet} accent="brand" />
        )}
        <KpiCard label="Open Positions" value={kpis.open_positions.toLocaleString()} icon={Briefcase} accent="brand" />
        <KpiCard label="Performance Score" value={`${kpis.avg_performance_score} / 5`} icon={Star} accent="healthy" />
        <KpiCard label="Satisfaction Score" value={`${kpis.avg_satisfaction_score} / 5`} icon={Heart} accent="healthy" />
        <KpiCard label="Attendance" value={`${kpis.avg_attendance_pct}%`} icon={CalendarCheck} accent="brand" />
        {kpis.avg_recruitment_cost_usd !== undefined && (
          <KpiCard label="Avg. Recruitment Cost" value={`$${kpis.avg_recruitment_cost_usd.toLocaleString()}`} icon={Wallet} accent="warning" />
        )}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="glass-card p-5 lg:col-span-2">
          <h3 className="mb-1 text-sm font-semibold text-ink-primary">Hiring Trend</h3>
          <p className="mb-4 text-xs text-ink-muted">New hires by month, most recent 12 months</p>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={data.hiring_trend}>
              <defs>
                <linearGradient id="hireGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#7C9EFF" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#7C9EFF" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#253347" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="month" stroke="#5B6B85" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="#5B6B85" fontSize={11} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ background: "#121B2E", border: "1px solid #253347", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#E8EDF6" }}
              />
              <Area type="monotone" dataKey="hires" stroke="#7C9EFF" strokeWidth={2} fill="url(#hireGradient)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-card p-5">
          <h3 className="mb-1 text-sm font-semibold text-ink-primary">Headcount by Department</h3>
          <p className="mb-4 text-xs text-ink-muted">Active employees</p>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={data.department_distribution}
                dataKey="headcount"
                nameKey="department"
                innerRadius={55}
                outerRadius={90}
                paddingAngle={2}
              >
                {data.department_distribution.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} stroke="#0B1220" strokeWidth={2} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#121B2E", border: "1px solid #253347", borderRadius: 8, fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-2 grid grid-cols-2 gap-x-3 gap-y-1.5">
            {data.department_distribution.map((d, i) => (
              <div key={d.department} className="flex items-center gap-1.5 text-[11px] text-ink-secondary">
                <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: PIE_COLORS[i % PIE_COLORS.length] }} />
                <span className="truncate">{d.department}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4 glass-card p-5">
        <h3 className="mb-1 text-sm font-semibold text-ink-primary">Hires per Month</h3>
        <p className="mb-4 text-xs text-ink-muted">Bar view of the same hiring trend, for quick month-over-month comparison</p>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data.hiring_trend}>
            <CartesianGrid stroke="#253347" strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="month" stroke="#5B6B85" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis stroke="#5B6B85" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ background: "#121B2E", border: "1px solid #253347", borderRadius: 8, fontSize: 12 }} />
            <Bar dataKey="hires" fill="#6EE7C9" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
