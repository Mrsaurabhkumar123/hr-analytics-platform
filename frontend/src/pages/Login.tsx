import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Lock, Mail, ArrowRight, AlertCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { PulseMark, PulseLine } from "../components/PulseMark";

const DEMO_LOGINS = [
  { role: "Super Admin", email: "admin@hranalytics.io", password: "Admin@12345" },
  { role: "HR Admin", email: "hr.admin@hranalytics.io", password: "HrAdmin@123" },
  { role: "HR Manager", email: "hr.manager@hranalytics.io", password: "HrManager@123" },
];

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(email, password);
      navigate("/");
    } catch {
      setError("Incorrect email or password.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center text-center">
          <PulseMark className="mb-4 h-12 w-12" />
          <h1 className="font-display text-2xl font-semibold text-ink-primary">Pulse</h1>
          <p className="mt-1 text-sm text-ink-secondary">HR Analytics &amp; Employee Intelligence</p>
        </div>

        <form onSubmit={handleSubmit} className="glass-card space-y-4 p-6">
          {error && (
            <div className="flex items-center gap-2 rounded-lg border border-pulse-risk/30 bg-pulse-risk/10 px-3 py-2 text-xs text-pulse-risk">
              <AlertCircle className="h-3.5 w-3.5 shrink-0" />
              {error}
            </div>
          )}
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-secondary">Email</label>
            <div className="relative">
              <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-muted" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="input-field pl-9"
              />
            </div>
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-ink-secondary">Password</label>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-muted" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="input-field pl-9"
              />
            </div>
          </div>
          <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
            {isSubmitting ? "Signing in..." : "Sign in"}
            {!isSubmitting && <ArrowRight className="h-4 w-4" />}
          </button>
        </form>

        <div className="mt-5">
          <PulseLine className="mx-auto h-4 w-24 text-base-border" />
        </div>

        <div className="mt-5 rounded-xl border border-base-border bg-base-surface/40 p-4">
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-ink-muted">
            Demo credentials
          </p>
          <ul className="space-y-1.5 text-xs">
            {DEMO_LOGINS.map((d) => (
              <li key={d.email} className="flex items-center justify-between gap-2 font-mono text-ink-secondary">
                <span className="text-ink-muted">{d.role}</span>
                <button
                  type="button"
                  onClick={() => {
                    setEmail(d.email);
                    setPassword(d.password);
                  }}
                  className="rounded bg-base-alt px-1.5 py-0.5 text-brand hover:bg-base-alt/70"
                >
                  {d.email}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
