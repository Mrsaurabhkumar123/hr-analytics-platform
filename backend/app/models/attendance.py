from app.extensions import db


class AttendanceRecord(db.Model):
    """Daily attendance snapshot, aggregated monthly for the Attendance dashboard."""
    __tablename__ = "attendance_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    month = db.Column(db.String(7), nullable=False, index=True)  # 'YYYY-MM'

    present_days = db.Column(db.Integer, default=0)
    absent_days = db.Column(db.Integer, default=0)
    late_arrivals = db.Column(db.Integer, default=0)
    work_from_home_days = db.Column(db.Integer, default=0)
    overtime_hours = db.Column(db.Float, default=0.0)

    employee = db.relationship("Employee")

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "month": self.month,
            "present_days": self.present_days,
            "absent_days": self.absent_days,
            "late_arrivals": self.late_arrivals,
            "work_from_home_days": self.work_from_home_days,
            "overtime_hours": self.overtime_hours,
        }
