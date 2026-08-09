"""
Employee is the central entity of the platform. Fields here intentionally
cover everything the Executive, Attrition, Salary, and Performance
dashboards need, plus every feature the attrition-risk ML model consumes,
so a single query can drive most read-heavy dashboard endpoints without
N+1 joins.
"""
from datetime import date
from app.extensions import db


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False, index=True)

    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    gender = db.Column(db.String(20), nullable=False, default="Undisclosed")

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    department = db.relationship("Department", back_populates="employees")

    job_title = db.Column(db.String(120), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=True)
    manager = db.relationship("Employee", remote_side=[id], backref="direct_reports")

    joining_date = db.Column(db.Date, nullable=False)
    exit_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    attrited = db.Column(db.Boolean, default=False, nullable=False)
    exit_reason = db.Column(db.String(255), nullable=True)

    monthly_salary = db.Column(db.Numeric(12, 2), nullable=False)
    last_salary_hike_pct = db.Column(db.Float, default=0.0)
    promotions_count = db.Column(db.Integer, default=0)
    years_since_last_promotion = db.Column(db.Float, default=0.0)

    performance_score = db.Column(db.Float, default=3.0)   # 1.0 - 5.0
    satisfaction_score = db.Column(db.Float, default=3.0)  # 1.0 - 5.0
    attendance_pct = db.Column(db.Float, default=95.0)     # 0 - 100
    overtime_hours_monthly = db.Column(db.Float, default=0.0)
    leave_days_taken_ytd = db.Column(db.Integer, default=0)
    training_hours_ytd = db.Column(db.Float, default=0.0)
    distance_from_home_km = db.Column(db.Float, default=10.0)
    remote_ratio_pct = db.Column(db.Float, default=0.0)

    def tenure_years(self) -> float:
        end = self.exit_date or date.today()
        return round((end - self.joining_date).days / 365.25, 2)

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self, include_sensitive: bool = True) -> dict:
        data = {
            "id": self.id,
            "employee_code": self.employee_code,
            "full_name": self.full_name(),
            "email": self.email,
            "gender": self.gender,
            "department": self.department.name if self.department else None,
            "department_id": self.department_id,
            "job_title": self.job_title,
            "manager": self.manager.full_name() if self.manager else None,
            "joining_date": self.joining_date.isoformat() if self.joining_date else None,
            "tenure_years": self.tenure_years(),
            "is_active": self.is_active,
            "attrited": self.attrited,
            "performance_score": self.performance_score,
            "satisfaction_score": self.satisfaction_score,
            "attendance_pct": self.attendance_pct,
            "promotions_count": self.promotions_count,
            "training_hours_ytd": self.training_hours_ytd,
            "leave_days_taken_ytd": self.leave_days_taken_ytd,
        }
        if include_sensitive:
            data["monthly_salary"] = float(self.monthly_salary)
            data["last_salary_hike_pct"] = self.last_salary_hike_pct
            data["years_since_last_promotion"] = self.years_since_last_promotion
            data["overtime_hours_monthly"] = self.overtime_hours_monthly
            data["distance_from_home_km"] = self.distance_from_home_km
            data["remote_ratio_pct"] = self.remote_ratio_pct
            data["exit_reason"] = self.exit_reason
        return data

    def ml_feature_dict(self) -> dict:
        """Feature vector consumed by the attrition-risk model. Keep this
        in sync with app/ml/train_model.py FEATURE_COLUMNS."""
        return {
            "tenure_years": self.tenure_years(),
            "monthly_salary": float(self.monthly_salary),
            "last_salary_hike_pct": self.last_salary_hike_pct or 0.0,
            "promotions_count": self.promotions_count or 0,
            "years_since_last_promotion": self.years_since_last_promotion or 0.0,
            "performance_score": self.performance_score or 3.0,
            "satisfaction_score": self.satisfaction_score or 3.0,
            "attendance_pct": self.attendance_pct or 95.0,
            "overtime_hours_monthly": self.overtime_hours_monthly or 0.0,
            "leave_days_taken_ytd": self.leave_days_taken_ytd or 0,
            "training_hours_ytd": self.training_hours_ytd or 0.0,
            "distance_from_home_km": self.distance_from_home_km or 10.0,
            "remote_ratio_pct": self.remote_ratio_pct or 0.0,
        }
