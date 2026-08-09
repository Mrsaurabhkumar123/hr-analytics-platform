import { useEffect, useState } from "react";
import { AlertTriangle, Target, Gauge, ListChecks } from "lucide-react";
import { attritionApi } from "../api/client";
import type { RiskListResponse, RiskResult, ModelMetrics } from "../types";
import { PageHeader } from "../components/PageHeader";
import { KpiCard } from "../components/KpiCard";
import { RiskBadge } from "../components/RiskBadge";
import { LoadingState, ErrorState } from "../components/StateViews";

export function AttritionRisk() {
  const [risk, setRisk] = useState<RiskListResponse | null>(null);
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [selected, setSelected] = useState<RiskResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([attritionApi.risk(), attritionApi.modelMetrics()])
      .then(([r, m]) => {
        setRisk(r);
        setMetrics(m);
        setSelected(r.results[0] ?? null);
      })
      .catch((err) => {
        if (err?.response?.status === 503) {
          setError("The attrition model hasn't been trained yet. Run: python -m app.ml.train_model");
        } else {
          setError("Could not load attrition risk data.");
        }
      });
  }, []);

  if (error) return <div className="p-8"><ErrorState message={error} /></div>;
  if (!risk || !metrics) return <LoadingState />;

  return (
    <div className="p-8">
      <PageHeader
        title="AI Employee Risk Prediction"
        subtitle="Random Forest classifier trained on tenure, compensation, performance, attendance, and engagement signals"
      />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard label="Employees Scored" value={risk.count.toLocaleString()} icon={Target} accent="brand" />
        <KpiCard label="High Risk" value={risk.high_risk_count.toLocaleString()} icon={AlertTriangle} accent="risk" />
        <KpiCard label="Model Accuracy" value={`${(metrics.accuracy * 100).toFixed(1)}%`} icon={Gauge} accent="healthy" />
        <KpiCard label="ROC-AUC" value={metrics.roc_auc.toFixed(3)} icon={ListChecks} accent="brand" />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-5">
        <div className="glass-card overflow-hidden lg:col-span-3">
          <div className="border-b border-base-border px-5 py-4">
            <h3 className="text-sm font-semibold text-ink-primary">Ranked by Risk Score</h3>
            <p className="text-xs text-ink-muted">Click a row to see full reasoning and recommended actions</p>
          </div>
          <div className="max-h-[560px] overflow-y-auto">
            <table className="w-full text-left text-sm">
              <thead className="sticky top-0 bg-base-surface">
                <tr className="border-b border-base-border text-xs uppercase tracking-wide text-ink-muted">
                  <th className="px-4 py-2.5 font-medium">Employee</th>
                  <th className="px-4 py-2.5 font-medium">Department</th>
                  <th className="px-4 py-2.5 font-medium">Risk</th>
                  <th className="px-4 py-2.5 font-medium">Category</th>
                </tr>
              </thead>
              <tbody>
                {risk.results.map((r) => (
                  <tr
                    key={r.employee_id}
                    onClick={() => setSelected(r)}
                    className={`cursor-pointer border-b border-base-border/60 last:border-0 hover:bg-base-alt/40 ${
                      selected?.employee_id === r.employee_id ? "bg-base-alt/50" : ""
                    }`}
                  >
                    <td className="px-4 py-3">
                      <p className="font-medium text-ink-primary">{r.full_name}</p>
                      <p className="text-xs text-ink-muted">{r.employee_code} · {r.job_title}</p>
                    </td>
                    <td className="px-4 py-3 text-ink-secondary">{r.department}</td>
                    <td className="px-4 py-3 font-mono font-medium text-ink-primary">{r.risk_score_pct}%</td>
                    <td className="px-4 py-3">
                      <RiskBadge category={r.risk_category} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="lg:col-span-2">
          {selected ? (
            <div className="glass-card sticky top-4 p-5">
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <h3 className="font-display text-lg font-semibold text-ink-primary">{selected.full_name}</h3>
                  <p className="text-xs text-ink-muted">{selected.employee_code} · {selected.department}</p>
                </div>
                <RiskBadge category={selected.risk_category} />
              </div>

              <div className="mb-5 flex items-end gap-1">
                <span className="font-mono text-4xl font-semibold text-ink-primary">{selected.risk_score_pct}</span>
                <span className="mb-1 text-sm text-ink-muted">% resignation probability</span>
              </div>

              <div className="mb-4">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">Reasons</p>
                <ul className="space-y-1.5">
                  {selected.reasons.map((r) => (
                    <li key={r} className="flex items-start gap-2 text-sm text-ink-secondary">
                      <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-pulse-risk" />
                      {r}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">Suggested Actions</p>
                <ul className="space-y-1.5">
                  {selected.suggested_actions.map((a) => (
                    <li key={a} className="flex items-start gap-2 text-sm text-ink-secondary">
                      <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-pulse-healthy" />
                      {a}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="glass-card p-5 text-sm text-ink-muted">Select an employee to see risk details.</div>
          )}

          <div className="glass-card mt-4 p-5">
            <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-ink-muted">Top Feature Importance</p>
            <div className="space-y-2">
              {Object.entries(metrics.feature_importance)
                .slice(0, 6)
                .map(([feature, importance]) => (
                  <div key={feature}>
                    <div className="mb-1 flex justify-between text-xs text-ink-secondary">
                      <span>{feature.replace(/_/g, " ")}</span>
                      <span className="font-mono">{(importance * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-1.5 overflow-hidden rounded-full bg-base-alt">
                      <div className="h-full rounded-full bg-brand" style={{ width: `${importance * 100 * 3}%` }} />
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
