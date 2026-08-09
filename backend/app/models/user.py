"""
User model handles authentication and role-based access control.
Separated from Employee so system accounts (e.g. Super Admin) can exist
without necessarily being a payroll employee.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class Role:
    SUPER_ADMIN = "SUPER_ADMIN"
    HR_ADMIN = "HR_ADMIN"
    HR_MANAGER = "HR_MANAGER"
    DEPARTMENT_MANAGER = "DEPARTMENT_MANAGER"
    TEAM_LEAD = "TEAM_LEAD"
    EMPLOYEE = "EMPLOYEE"
    AUDITOR = "AUDITOR"

    ALL = [SUPER_ADMIN, HR_ADMIN, HR_MANAGER, DEPARTMENT_MANAGER, TEAM_LEAD, EMPLOYEE, AUDITOR]

    # Roles allowed to view org-wide sensitive analytics (salary, attrition risk)
    ANALYTICS_ROLES = [SUPER_ADMIN, HR_ADMIN, HR_MANAGER, DEPARTMENT_MANAGER, AUDITOR]

    # Roles allowed to write/manage employee records
    WRITE_ROLES = [SUPER_ADMIN, HR_ADMIN, HR_MANAGER]


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(30), nullable=False, default=Role.EMPLOYEE)

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_email_verified = db.Column(db.Boolean, default=False, nullable=False)
    two_factor_enabled = db.Column(db.Boolean, default=False, nullable=False)
    two_factor_secret = db.Column(db.String(64), nullable=True)

    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_email_verified": self.is_email_verified,
            "two_factor_enabled": self.two_factor_enabled,
            "employee_id": self.employee_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
