"""
Generates a realistic, internally-consistent synthetic HR dataset so the
platform is fully demoable without any customer data: departments, an
org hierarchy (manager chains), employees with correlated attrition-driving
attributes, plus attendance/leave/performance history, and the default
login users for each role.

Usage:
    python -m app.seed            # seed if empty
    python -m app.seed --reset    # drop + reseed everything
"""
import argparse
import random
from datetime import date, timedelta

from faker import Faker

from app import create_app
from app.extensions import db
from app.config import Config
from app.models.user import User, Role
from app.models.department import Department
from app.models.employee import Employee
from app.models.attendance import AttendanceRecord
from app.models.leave import LeaveRecord
from app.models.performance import PerformanceReview

fake = Faker()
random.seed(42)
Faker.seed(42)

DEPARTMENTS = [
    ("Engineering", 4_500_000),
    ("Sales", 2_800_000),
    ("Marketing", 1_600_000),
    ("Finance", 1_200_000),
    ("Human Resources", 900_000),
    ("Customer Support", 1_100_000),
    ("Product", 1_800_000),
    ("IT & Infrastructure", 1_400_000),
]

JOB_TITLES = {
    "Engineering": ["Software Engineer", "Senior Software Engineer", "Engineering Manager", "QA Engineer", "DevOps Engineer"],
    "Sales": ["Sales Executive", "Account Manager", "Sales Manager", "Business Development Rep"],
    "Marketing": ["Marketing Specialist", "Content Strategist", "Marketing Manager", "SEO Analyst"],
    "Finance": ["Financial Analyst", "Accountant", "Finance Manager", "Payroll Specialist"],
    "Human Resources": ["HR Generalist", "HR Business Partner", "Talent Acquisition Specialist", "HR Manager"],
    "Customer Support": ["Support Associate", "Support Team Lead", "Customer Success Manager"],
    "Product": ["Product Manager", "Product Analyst", "UX Researcher", "Product Designer"],
    "IT & Infrastructure": ["IT Support Specialist", "Systems Administrator", "Network Engineer", "IT Manager"],
}

LEAVE_TYPES = ["Sick", "Paid", "Casual", "Unpaid"]
EXIT_REASONS = [
    "Better opportunity elsewhere", "Compensation", "Relocation", "Career growth",
    "Work-life balance", "Management issues", "Retirement", "Performance",
]


def _random_date(start_year=2016, end=None):
    end = end or date.today()
    start = date(start_year, 1, 1)
    return start + timedelta(days=random.randint(0, (end - start).days))


def _build_employee(department_id, department_name, code_seq):
    joining_date = _random_date(2017)
    tenure_years = (date.today() - joining_date).days / 365.25

    # Correlated, "realistic" attrition-driving attributes: employees with
    # lower salary hikes, no promotions, poor attendance, and low
    # satisfaction are deliberately biased toward attrited=True so the ML
    # model has real signal to learn (not random noise).
    performance_score = round(random.gauss(3.4, 0.7), 2)
    performance_score = min(max(performance_score, 1.0), 5.0)
    satisfaction_score = round(random.gauss(3.3, 0.9), 2)
    satisfaction_score = min(max(satisfaction_score, 1.0), 5.0)
    attendance_pct = round(min(max(random.gauss(93, 6), 55), 100), 1)
    promotions_count = random.choices([0, 1, 2, 3], weights=[45, 30, 18, 7])[0]
    years_since_promo = round(random.uniform(0, tenure_years), 1) if promotions_count else round(tenure_years, 1)
    last_hike_pct = round(max(random.gauss(7, 5), -2), 1)
    leave_days = random.randint(0, 30)
    overtime_hours = round(max(random.gauss(8, 6), 0), 1)
    training_hours = round(max(random.gauss(22, 15), 0), 1)
    distance_km = round(max(random.gauss(14, 9), 0.5), 1)
    remote_ratio = random.choice([0, 0, 0, 20, 40, 60, 100])

    base_salary = {
        "Engineering": 6800, "Sales": 4800, "Marketing": 4600, "Finance": 5200,
        "Human Resources": 4400, "Customer Support": 3800, "Product": 6200,
        "IT & Infrastructure": 5400,
    }.get(department_name, 5000)
    monthly_salary = round(base_salary * (0.75 + tenure_years * 0.03) * random.uniform(0.85, 1.25), 2)

    risk_score = (
        (5 - satisfaction_score) * 0.25
        + (100 - attendance_pct) * 0.01
        + (1 if promotions_count == 0 and tenure_years > 2 else 0) * 0.9
        + (5 - performance_score) * 0.15
        + max(0, (6 - last_hike_pct)) * 0.03
    )
    attrited = random.random() < min(max(risk_score / 6, 0.03), 0.65)

    exit_date, exit_reason, is_active = None, None, True
    if attrited:
        exit_date = joining_date + timedelta(days=random.randint(180, max(int((date.today() - joining_date).days), 200)))
        if exit_date >= date.today():
            exit_date = date.today() - timedelta(days=random.randint(1, 200))
        exit_reason = random.choice(EXIT_REASONS)
        is_active = False

    first, last = fake.first_name(), fake.last_name()
    return Employee(
        employee_code=f"EMP{code_seq:05d}",
        first_name=first,
        last_name=last,
        email=f"{first.lower()}.{last.lower()}{code_seq}@hranalytics.io",
        gender=random.choice(["Female", "Male", "Non-binary", "Undisclosed"]),
        department_id=department_id,
        job_title=random.choice(JOB_TITLES[department_name]),
        joining_date=joining_date,
        exit_date=exit_date,
        is_active=is_active,
        attrited=attrited,
        exit_reason=exit_reason,
        monthly_salary=monthly_salary,
        last_salary_hike_pct=last_hike_pct,
        promotions_count=promotions_count,
        years_since_last_promotion=years_since_promo,
        performance_score=performance_score,
        satisfaction_score=satisfaction_score,
        attendance_pct=attendance_pct,
        overtime_hours_monthly=overtime_hours,
        leave_days_taken_ytd=leave_days,
        training_hours_ytd=training_hours,
        distance_from_home_km=distance_km,
        remote_ratio_pct=remote_ratio,
    )


def seed(reset: bool = False):
    app = create_app()
    with app.app_context():
        if reset:
            db.drop_all()
        db.create_all()

        if not reset and Employee.query.first():
            print("Database already has data. Use --reset to wipe and reseed.")
            return

        departments = {}
        for name, budget in DEPARTMENTS:
            d = Department(name=name, annual_budget=budget)
            db.session.add(d)
            departments[name] = d
        db.session.commit()

        employees = []
        code_seq = 1
        for name, _ in DEPARTMENTS:
            count = Config.SEED_EMPLOYEE_COUNT // len(DEPARTMENTS)
            for _ in range(count):
                emp = _build_employee(departments[name].id, name, code_seq)
                employees.append(emp)
                code_seq += 1
        db.session.add_all(employees)
        db.session.commit()

        # Assign ~1 in 12 active employees as a manager for a subset of others
        # so the org chart / Employee 360 "manager" field is populated.
        active = [e for e in employees if e.is_active]
        managers = random.sample(active, max(len(active) // 12, 1))
        for e in active:
            if e not in managers and random.random() < 0.85:
                e.manager_id = random.choice(managers).id
        db.session.commit()

        # Attendance + leave + performance history for active employees
        # (last 6 months) to power the Attendance/Leave/Performance dashboards.
        months = []
        cursor = date.today().replace(day=1)
        for _ in range(6):
            months.append(f"{cursor.year}-{cursor.month:02d}")
            cursor = (cursor.replace(day=1) - timedelta(days=1)).replace(day=1)

        for e in active:
            for m in months:
                present = random.randint(16, 22)
                db.session.add(AttendanceRecord(
                    employee_id=e.id, month=m,
                    present_days=present,
                    absent_days=max(0, 22 - present - random.randint(0, 2)),
                    late_arrivals=random.randint(0, 5),
                    work_from_home_days=random.randint(0, 8) if e.remote_ratio_pct else 0,
                    overtime_hours=round(max(random.gauss(e.overtime_hours_monthly, 3), 0), 1),
                ))
            if random.random() < 0.4:
                start = _random_date(2025)
                db.session.add(LeaveRecord(
                    employee_id=e.id,
                    leave_type=random.choice(LEAVE_TYPES),
                    start_date=start,
                    end_date=start + timedelta(days=random.randint(1, 5)),
                    status=random.choice(["APPROVED", "APPROVED", "APPROVED", "PENDING"]),
                ))
            db.session.add(PerformanceReview(
                employee_id=e.id,
                review_period="2026-Q2",
                kpi_achievement_pct=round(min(max(random.gauss(85, 15), 30), 130), 1),
                rating=e.performance_score,
                reviewer_comments=fake.sentence(nb_words=10),
            ))
        db.session.commit()

        # Default login users, one per role, for demoing RBAC.
        demo_users = [
            (Config.DEFAULT_ADMIN_EMAIL, "System Administrator", Role.SUPER_ADMIN, Config.DEFAULT_ADMIN_PASSWORD),
            ("hr.admin@hranalytics.io", "Priya Nair", Role.HR_ADMIN, "HrAdmin@123"),
            ("hr.manager@hranalytics.io", "Daniel Cooper", Role.HR_MANAGER, "HrManager@123"),
            ("dept.manager@hranalytics.io", "Wei Zhang", Role.DEPARTMENT_MANAGER, "DeptMgr@123"),
            ("team.lead@hranalytics.io", "Sara Ahmed", Role.TEAM_LEAD, "TeamLead@123"),
            ("employee@hranalytics.io", "Alex Johnson", Role.EMPLOYEE, "Employee@123"),
            ("auditor@hranalytics.io", "Grace Kim", Role.AUDITOR, "Auditor@123"),
        ]
        for email, name, role, pwd in demo_users:
            u = User(email=email, full_name=name, role=role, is_email_verified=True)
            u.set_password(pwd)
            db.session.add(u)
        db.session.commit()

        print(f"Seeded {len(employees)} employees across {len(DEPARTMENTS)} departments.")
        print(f"Attrited: {sum(1 for e in employees if e.attrited)} | Active: {sum(1 for e in employees if e.is_active)}")
        print("Demo logins (all roles share domain @hranalytics.io):")
        for email, _, role, pwd in demo_users:
            print(f"  {role:<20} {email:<32} {pwd}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Drop all tables and reseed from scratch")
    args = parser.parse_args()
    seed(reset=args.reset)
