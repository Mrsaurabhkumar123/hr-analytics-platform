from app.extensions import db


class LeaveRecord(db.Model):
    __tablename__ = "leave_records"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    leave_type = db.Column(db.String(30), nullable=False)  # Sick, Paid, Unpaid, Casual
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="APPROVED")  # PENDING, APPROVED, REJECTED

    employee = db.relationship("Employee")

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "leave_type": self.leave_type,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status": self.status,
        }
