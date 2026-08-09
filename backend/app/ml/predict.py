"""
Loads the trained attrition model and turns a raw probability into the
Risk Score / Risk Category / Reasons / Suggested Actions shape the
Attrition Risk dashboard displays. Reasons are derived from the model's
global feature importances applied to how far this employee's own values
sit from a healthy baseline -- a lightweight, explainable alternative to
full SHAP values that's cheap enough to run per-request.
"""
import json
import os

import joblib
import pandas as pd

from app.config import Config
from app.ml.train_model import FEATURE_COLUMNS

_MODEL_CACHE = {"bundle": None, "metrics": None}

# (feature, "healthy" direction, human label, suggested action)
REASON_RULES = [
    ("monthly_salary", "low", "Below-market salary for role/tenure", "Salary Review"),
    ("attendance_pct", "low", "Poor attendance", "HR Discussion"),
    ("years_since_last_promotion", "high", "No recent promotion", "Promotion / Career Path Review"),
    ("performance_score", "low", "Declining performance score", "Coaching & Performance Plan"),
    ("leave_days_taken_ytd", "high", "High leave usage", "Workload & Wellbeing Check-in"),
    ("satisfaction_score", "low", "Low engagement / satisfaction score", "Manager 1:1 & Engagement Survey"),
    ("overtime_hours_monthly", "high", "Sustained overtime", "Flexible Work / Workload Rebalancing"),
    ("training_hours_ytd", "low", "Minimal training investment", "Enroll in Training / Upskilling"),
    ("last_salary_hike_pct", "low", "Below-average last salary hike", "Compensation Adjustment"),
    ("distance_from_home_km", "high", "Long commute", "Remote / Hybrid Flexibility"),
]

# Population medians used as the "healthy" reference point for reason
# generation. Recomputed from training data at train time in a full
# production system; hard-coded demo baseline here for simplicity.
BASELINE = {
    "monthly_salary": 5200,
    "attendance_pct": 94,
    "years_since_last_promotion": 1.5,
    "performance_score": 3.6,
    "leave_days_taken_ytd": 10,
    "satisfaction_score": 3.6,
    "overtime_hours_monthly": 6,
    "training_hours_ytd": 20,
    "last_salary_hike_pct": 6,
    "distance_from_home_km": 15,
}


def _load_bundle():
    if _MODEL_CACHE["bundle"] is None:
        if not os.path.exists(Config.ML_MODEL_PATH):
            raise FileNotFoundError(
                "No trained model found. Run: python -m app.ml.train_model"
            )
        _MODEL_CACHE["bundle"] = joblib.load(Config.ML_MODEL_PATH)
    if _MODEL_CACHE["metrics"] is None and os.path.exists(Config.ML_METRICS_PATH):
        with open(Config.ML_METRICS_PATH) as f:
            _MODEL_CACHE["metrics"] = json.load(f)
    return _MODEL_CACHE["bundle"], _MODEL_CACHE["metrics"]


def get_model_metrics():
    _, metrics = _load_bundle()
    return metrics


def _risk_category(score_pct: float) -> str:
    if score_pct >= 70:
        return "HIGH RISK"
    if score_pct >= 40:
        return "MEDIUM RISK"
    return "LOW RISK"


def _reasons_and_actions(feature_values: dict, top_n: int = 4):
    scored = []
    for feature, direction, label, action in REASON_RULES:
        baseline = BASELINE.get(feature)
        value = feature_values.get(feature)
        if baseline is None or value is None:
            continue
        if direction == "low":
            severity = max(0.0, (baseline - value) / baseline) if baseline else 0
        else:
            severity = max(0.0, (value - baseline) / baseline) if baseline else 0
        if severity > 0.05:
            scored.append((severity, label, action))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_n]
    reasons = [label for _, label, _ in top]
    actions = list(dict.fromkeys(action for _, _, action in top))  # de-dup, keep order
    if not reasons:
        reasons = ["No significant risk indicators detected"]
        actions = ["Continue Standard Engagement"]
    return reasons, actions


def predict_risk(employee) -> dict:
    bundle, _ = _load_bundle()
    model, features = bundle["model"], bundle["features"]

    feature_values = employee.ml_feature_dict()
    X = pd.DataFrame([[feature_values[f] for f in features]], columns=features)
    probability = float(model.predict_proba(X)[0, 1])
    score_pct = round(probability * 100, 1)

    reasons, actions = _reasons_and_actions(feature_values)

    return {
        "employee_id": employee.id,
        "employee_code": employee.employee_code,
        "full_name": employee.full_name(),
        "department": employee.department.name if employee.department else None,
        "job_title": employee.job_title,
        "risk_score_pct": score_pct,
        "risk_category": _risk_category(score_pct),
        "reasons": reasons,
        "suggested_actions": actions,
    }


def predict_risk_bulk(employees) -> list:
    bundle, _ = _load_bundle()
    model, features = bundle["model"], bundle["features"]

    rows = [e.ml_feature_dict() for e in employees]
    X = pd.DataFrame(rows, columns=features)
    probabilities = model.predict_proba(X)[:, 1]

    results = []
    for employee, probability in zip(employees, probabilities):
        score_pct = round(float(probability) * 100, 1)
        reasons, actions = _reasons_and_actions(employee.ml_feature_dict())
        results.append({
            "employee_id": employee.id,
            "employee_code": employee.employee_code,
            "full_name": employee.full_name(),
            "department": employee.department.name if employee.department else None,
            "job_title": employee.job_title,
            "risk_score_pct": score_pct,
            "risk_category": _risk_category(score_pct),
            "reasons": reasons,
            "suggested_actions": actions,
        })
    results.sort(key=lambda r: r["risk_score_pct"], reverse=True)
    return results
