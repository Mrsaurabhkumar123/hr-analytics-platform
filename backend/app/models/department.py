from app.extensions import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    annual_budget = db.Column(db.Numeric(14, 2), default=0)

    employees = db.relationship("Employee", back_populates="department", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "annual_budget": float(self.annual_budget) if self.annual_budget is not None else 0,
            "headcount": self.employees.filter_by(is_active=True).count(),
        }
