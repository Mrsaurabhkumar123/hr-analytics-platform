"""
Employee Directory & Profile endpoints: search, filter, sort, pagination,
CSV export, and the Employee 360 profile view.
"""
import csv
import io

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import or_

from app.extensions import db
from app.models.employee import Employee
from app.models.department import Department
from app.models.user import Role
from app.utils.decorators import roles_required
from app.utils.validators import paginate_args

employees_bp = Blueprint("employees", __name__)


def _visible_salary(claims) -> bool:
    return claims.get("role") in Role.ANALYTICS_ROLES + [Role.SUPER_ADMIN]


@employees_bp.get("")
@jwt_required()
def list_employees():
    claims = get_jwt()
    page, per_page = paginate_args(request)

    query = Employee.query
    search = request.args.get("q", "").strip()
    if search:
        like = f"%{search}%"
        query = query.join(Department, isouter=True).filter(
            or_(
                Employee.first_name.ilike(like),
                Employee.last_name.ilike(like),
                Employee.email.ilike(like),
                Employee.employee_code.ilike(like),
                Employee.job_title.ilike(like),
                Department.name.ilike(like),
            )
        )

    department_id = request.args.get("department_id")
    if department_id:
        query = query.filter(Employee.department_id == int(department_id))

    status = request.args.get("status")
    if status == "active":
        query = query.filter(Employee.is_active.is_(True))
    elif status == "exited":
        query = query.filter(Employee.is_active.is_(False))

    sort_field = request.args.get("sort_by", "employee_code")
    sort_dir = request.args.get("sort_dir", "asc")
    sortable = {
        "employee_code": Employee.employee_code,
        "full_name": Employee.first_name,
        "department": Department.name,
        "performance_score": Employee.performance_score,
        "joining_date": Employee.joining_date,
        "monthly_salary": Employee.monthly_salary,
    }
    sort_column = sortable.get(sort_field, Employee.employee_code)
    query = query.order_by(sort_column.desc() if sort_dir == "desc" else sort_column.asc())

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    include_salary = _visible_salary(claims)

    return jsonify({
        "items": [e.to_dict(include_sensitive=include_salary) for e in items],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": (total + per_page - 1) // per_page,
    })


@employees_bp.get("/export")
@jwt_required()
@roles_required(Role.SUPER_ADMIN, Role.HR_ADMIN, Role.HR_MANAGER, Role.AUDITOR)
def export_employees_csv():
    employees = Employee.query.order_by(Employee.employee_code.asc()).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "Employee Code", "Full Name", "Email", "Department", "Job Title",
        "Joining Date", "Tenure (yrs)", "Status", "Performance", "Satisfaction",
        "Attendance %", "Monthly Salary",
    ])
    for e in employees:
        writer.writerow([
            e.employee_code, e.full_name(), e.email,
            e.department.name if e.department else "",
            e.job_title, e.joining_date, e.tenure_years(),
            "Active" if e.is_active else "Exited",
            e.performance_score, e.satisfaction_score, e.attendance_pct,
            float(e.monthly_salary),
        ])
    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=employee_directory.csv"},
    )


@employees_bp.get("/<int:employee_id>")
@jwt_required()
def get_employee(employee_id):
    claims = get_jwt()
    employee = Employee.query.get_or_404(employee_id)
    include_salary = _visible_salary(claims)
    data = employee.to_dict(include_sensitive=include_salary)
    data["direct_reports"] = [r.to_dict(include_sensitive=False) for r in employee.direct_reports]
    return jsonify(data)
