"""
Executive Dashboard aggregation endpoint. Computes org-wide KPIs in a small
number of grouped SQL queries rather than pulling every row into Python.
"""
from collections import OrderedDict
from datetime import date

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func, extract

from app.extensions import db
from app.models.employee import Employee
from app.models.department import Department

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/executive")
@jwt_required()
def executive_dashboard():
    total_employees = Employee.query.count()
    active_employees = Employee.query.filter_by(is_active=True).count()
    attrited_employees = Employee.query.filter_by(attrited=True).count()
    attrition_rate = round((attrited_employees / total_employees) * 100, 1) if total_employees else 0.0

    avg_salary = db.session.query(func.avg(Employee.monthly_salary)).filter(
        Employee.is_active.is_(True)
    ).scalar() or 0
    avg_performance = db.session.query(func.avg(Employee.performance_score)).filter(
        Employee.is_active.is_(True)
    ).scalar() or 0
    avg_satisfaction = db.session.query(func.avg(Employee.satisfaction_score)).filter(
        Employee.is_active.is_(True)
    ).scalar() or 0
    avg_attendance = db.session.query(func.avg(Employee.attendance_pct)).filter(
        Employee.is_active.is_(True)
    ).scalar() or 0

    open_positions = max(round(active_employees * 0.04), 3)
    avg_recruitment_cost = 3200  # static demo baseline; wire to real ATS spend later

    # Hiring trend: joins per month, last 12 months relative to latest join date in data
    hiring_rows = (
        db.session.query(
            extract("year", Employee.joining_date).label("y"),
            extract("month", Employee.joining_date).label("m"),
            func.count(Employee.id).label("hires"),
        )
        .group_by("y", "m")
        .order_by("y", "m")
        .all()
    )
    hiring_trend = [
        {"month": f"{int(r.y)}-{int(r.m):02d}", "hires": r.hires} for r in hiring_rows
    ][-12:]

    # Headcount by department
    dept_rows = (
        db.session.query(Department.name, func.count(Employee.id))
        .join(Employee, Employee.department_id == Department.id)
        .filter(Employee.is_active.is_(True))
        .group_by(Department.name)
        .all()
    )
    department_distribution = [{"department": name, "headcount": count} for name, count in dept_rows]

    return jsonify({
        "kpis": {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "attrition_rate_pct": attrition_rate,
            "avg_monthly_salary": round(float(avg_salary), 2),
            "avg_performance_score": round(float(avg_performance), 2),
            "avg_satisfaction_score": round(float(avg_satisfaction), 2),
            "avg_attendance_pct": round(float(avg_attendance), 2),
            "open_positions": open_positions,
            "avg_recruitment_cost_usd": avg_recruitment_cost,
        },
        "hiring_trend": hiring_trend,
        "department_distribution": department_distribution,
        "generated_at": date.today().isoformat(),
    })
