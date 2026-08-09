from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models.department import Department
from app.models.employee import Employee

departments_bp = Blueprint("departments", __name__)


@departments_bp.get("")
@jwt_required()
def list_departments():
    departments = Department.query.order_by(Department.name.asc()).all()
    return jsonify([d.to_dict() for d in departments])


@departments_bp.get("/<int:department_id>/stats")
@jwt_required()
def department_stats(department_id):
    department = Department.query.get_or_404(department_id)
    active = Employee.query.filter_by(department_id=department_id, is_active=True)

    headcount = active.count()
    avg_salary = active.with_entities(func.avg(Employee.monthly_salary)).scalar() or 0
    avg_performance = active.with_entities(func.avg(Employee.performance_score)).scalar() or 0
    avg_attendance = active.with_entities(func.avg(Employee.attendance_pct)).scalar() or 0

    total_ever = Employee.query.filter_by(department_id=department_id).count()
    attrited = Employee.query.filter_by(department_id=department_id, attrited=True).count()
    attrition_rate = round((attrited / total_ever) * 100, 1) if total_ever else 0.0

    return jsonify({
        "department": department.to_dict(),
        "headcount": headcount,
        "avg_salary": round(float(avg_salary), 2),
        "avg_performance": round(float(avg_performance), 2),
        "avg_attendance_pct": round(float(avg_attendance), 2),
        "attrition_rate_pct": attrition_rate,
    })
