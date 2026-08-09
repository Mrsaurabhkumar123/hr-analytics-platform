"""
Attrition Dashboard + AI Employee Risk Prediction endpoints.

/trend, /heatmap        -> historical attrition analytics (Attrition Dashboard)
/risk                   -> live ML risk scores for all active employees
/risk/<employee_id>     -> risk score for a single employee (Employee 360 profile)
/model/metrics          -> accuracy / precision / recall / F1 / ROC-AUC / feature importance
"""
from collections import defaultdict

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import extract, func

from app.extensions import db
from app.models.employee import Employee
from app.models.department import Department
from app.models.user import Role
from app.utils.decorators import roles_required
from app.ml.predict import predict_risk, predict_risk_bulk, get_model_metrics

attrition_bp = Blueprint("attrition", __name__)

TENURE_BUCKETS = [
    (0, 1, "0-1 yrs"),
    (1, 3, "1-3 yrs"),
    (3, 5, "3-5 yrs"),
    (5, 10, "5-10 yrs"),
    (10, 999, "10+ yrs"),
]
SALARY_BUCKETS = [
    (0, 3000, "< $3k"),
    (3000, 5000, "$3k-5k"),
    (5000, 8000, "$5k-8k"),
    (8000, 12000, "$8k-12k"),
    (12000, 10 ** 9, "$12k+"),
]


def _bucket(value, buckets):
    for lo, hi, label in buckets:
        if lo <= value < hi:
            return label
    return buckets[-1][2]


@attrition_bp.get("/trend")
@jwt_required()
@roles_required(Role.SUPER_ADMIN, Role.HR_ADMIN, Role.HR_MANAGER, Role.DEPARTMENT_MANAGER, Role.AUDITOR)
def attrition_trend():
    rows = (
        db.session.query(
            extract("year", Employee.exit_date).label("y"),
            extract("month", Employee.exit_date).label("m"),
            func.count(Employee.id).label("exits"),
        )
        .filter(Employee.attrited.is_(True), Employee.exit_date.isnot(None))
        .group_by("y", "m")
        .order_by("y", "m")
        .all()
    )
    trend = [{"month": f"{int(r.y)}-{int(r.m):02d}", "exits": r.exits} for r in rows][-12:]

    by_department = (
        db.session.query(Department.name, func.count(Employee.id))
        .join(Employee, Employee.department_id == Department.id)
        .filter(Employee.attrited.is_(True))
        .group_by(Department.name)
        .all()
    )

    return jsonify({
        "monthly_trend": trend,
        "by_department": [{"department": n, "exits": c} for n, c in by_department],
    })


@attrition_bp.get("/heatmap")
@jwt_required()
@roles_required(Role.SUPER_ADMIN, Role.HR_ADMIN, Role.HR_MANAGER, Role.DEPARTMENT_MANAGER, Role.AUDITOR)
def attrition_heatmap():
    """Attrition rate cross-tabulated by department x tenure bucket, plus
    breakdowns by experience (tenure) and salary band for the Attrition
    Dashboard's experience/salary views."""
    employees = Employee.query.all()

    matrix = defaultdict(lambda: {"total": 0, "attrited": 0})
    tenure_summary = defaultdict(lambda: {"total": 0, "attrited": 0})
    salary_summary = defaultdict(lambda: {"total": 0, "attrited": 0})

    for e in employees:
        dept = e.department.name if e.department else "Unassigned"
        tenure_label = _bucket(e.tenure_years(), TENURE_BUCKETS)
        salary_label = _bucket(float(e.monthly_salary), SALARY_BUCKETS)

        key = (dept, tenure_label)
        matrix[key]["total"] += 1
        tenure_summary[tenure_label]["total"] += 1
        salary_summary[salary_label]["total"] += 1
        if e.attrited:
            matrix[key]["attrited"] += 1
            tenure_summary[tenure_label]["attrited"] += 1
            salary_summary[salary_label]["attrited"] += 1

    def rate(d):
        return round((d["attrited"] / d["total"]) * 100, 1) if d["total"] else 0.0

    heatmap = [
        {"department": dept, "tenure_bucket": tenure, "attrition_rate_pct": rate(v), "total": v["total"]}
        for (dept, tenure), v in matrix.items()
    ]
    by_experience = [
        {"tenure_bucket": label, "attrition_rate_pct": rate(tenure_summary[label]), "total": tenure_summary[label]["total"]}
        for _, _, label in TENURE_BUCKETS if label in tenure_summary
    ]
    by_salary = [
        {"salary_band": label, "attrition_rate_pct": rate(salary_summary[label]), "total": salary_summary[label]["total"]}
        for _, _, label in SALARY_BUCKETS if label in salary_summary
    ]

    return jsonify({"heatmap": heatmap, "by_experience": by_experience, "by_salary": by_salary})


@attrition_bp.get("/risk")
@jwt_required()
@roles_required(Role.SUPER_ADMIN, Role.HR_ADMIN, Role.HR_MANAGER, Role.DEPARTMENT_MANAGER)
def all_risk_scores():
    employees = Employee.query.filter_by(is_active=True).all()
    try:
        results = predict_risk_bulk(employees)
    except FileNotFoundError as exc:
        return jsonify({"error": "model_not_trained", "message": str(exc)}), 503
    return jsonify({
        "count": len(results),
        "high_risk_count": sum(1 for r in results if r["risk_category"] == "HIGH RISK"),
        "results": results,
    })


@attrition_bp.get("/risk/<int:employee_id>")
@jwt_required()
def employee_risk(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    try:
        return jsonify(predict_risk(employee))
    except FileNotFoundError as exc:
        return jsonify({"error": "model_not_trained", "message": str(exc)}), 503


@attrition_bp.get("/model/metrics")
@jwt_required()
@roles_required(Role.SUPER_ADMIN, Role.HR_ADMIN, Role.HR_MANAGER)
def model_metrics():
    metrics = get_model_metrics()
    if not metrics:
        return jsonify({"error": "model_not_trained", "message": "Model has not been trained yet."}), 503
    return jsonify(metrics)
