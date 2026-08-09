import { NavLink } from "react-router-dom";
import {
  LayoutGrid, Users, TrendingDown, Building2, Wallet, CalendarClock,
  GraduationCap, ClipboardCheck, UserSearch, LogOut,
} from "lucide-react";
import { PulseMark } from "./PulseMark";
import { useAuth } from "../context/AuthContext";

const BUILT_NAV = [
  { to: "/", label: "Executive", icon: LayoutGrid, end: true },
  { to: "/employees", label: "Employee Directory", icon: Users },
  { to: "/attrition-risk", label: "AI Attrition Risk", icon: TrendingDown },
];

// Present in the sidebar per the product spec, but not yet built in this
// slice -- shown honestly as disabled "Coming soon" items rather than
// wired to fake data, so the roadmap is visible without pretending these
// dashboards are functional.
const PLANNED_NAV = [
  { label: "Departments", icon: Building2 },
  { label: "Salary", icon: Wallet },
  { label: "Leave", icon: CalendarClock },
  { label: "Training", icon: GraduationCap },
  { label: "Recruitment", icon: UserSearch },
  { label: "Performance", icon: ClipboardCheck },
];

export function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col border-r border-base-border bg-base-surface/60 backdrop-blur-xl">
      <div className="flex items-center gap-2.5 px-5 py-5">
        <PulseMark />
        <div>
          <p className="font-display text-base font-semibold leading-none text-ink-primary">Pulse</p>
          <p className="mt-1 text-[11px] leading-none text-ink-muted">HR Intelligence Platform</p>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-2">
        <p className="px-2.5 pb-2 pt-3 text-[11px] font-semibold uppercase tracking-wider text-ink-muted">
          Dashboards
        </p>
        <ul className="space-y-0.5">
          {BUILT_NAV.map(({ to, label, icon: Icon, end }) => (
            <li key={to}>
              <NavLink
                to={to}
                end={end}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-brand/15 text-brand"
                      : "text-ink-secondary hover:bg-base-alt hover:text-ink-primary"
                  }`
                }
              >
                <Icon className="h-4 w-4" />
                {label}
              </NavLink>
            </li>
          ))}
        </ul>

        <p className="px-2.5 pb-2 pt-5 text-[11px] font-semibold uppercase tracking-wider text-ink-muted">
          Coming soon
        </p>
        <ul className="space-y-0.5">
          {PLANNED_NAV.map(({ label, icon: Icon }) => (
            <li key={label}>
              <div className="flex cursor-not-allowed items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium text-ink-muted/60">
                <Icon className="h-4 w-4" />
                {label}
              </div>
            </li>
          ))}
        </ul>
      </nav>

      <div className="border-t border-base-border px-4 py-4">
        <div className="mb-3 flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand/20 text-xs font-semibold text-brand">
            {user?.full_name?.slice(0, 2).toUpperCase()}
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-ink-primary">{user?.full_name}</p>
            <p className="truncate text-[11px] text-ink-muted">{user?.role.replace(/_/g, " ")}</p>
          </div>
        </div>
        <button onClick={logout} className="btn-secondary w-full text-xs">
          <LogOut className="h-3.5 w-3.5" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
