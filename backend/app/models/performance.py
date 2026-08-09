from app.extensions import db


class PerformanceReview(db.Model):
    __tablename__ = "performance_reviews"

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    review_period = db.Column(db.String(20), nullable=False)  # e.g. '2026-Q2'
    kpi_achievement_pct = db.Column(db.Float, default=0.0)
    rating = db.Column(db.Float, default=3.0)  # 1.0 - 5.0
    reviewer_comments = db.Column(db.Text, nullable=True)

    employee = db.relationship("Employee")

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "review_period": self.review_period,
            "kpi_achievement_pct": self.kpi_achievement_pct,
            "rating": self.rating,
            "reviewer_comments": self.reviewer_comments,
        }
