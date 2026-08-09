import { AlertTriangle, AlertCircle, CheckCircle2 } from "lucide-react";
import type { RiskCategory } from "../types";

export function RiskBadge({ category }: { category: RiskCategory }) {
  if (category === "HIGH RISK") {
    return (
      <span className="badge-high">
        <AlertTriangle className="h-3 w-3" /> High risk
      </span>
    );
  }
  if (category === "MEDIUM RISK") {
    return (
      <span className="badge-medium">
        <AlertCircle className="h-3 w-3" /> Medium risk
      </span>
    );
  }
  return (
    <span className="badge-low">
      <CheckCircle2 className="h-3 w-3" /> Low risk
    </span>
  );
}
