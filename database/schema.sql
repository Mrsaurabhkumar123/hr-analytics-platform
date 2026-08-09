-- =====================================================================
-- Reference schema (MySQL 8+) for the HR Analytics Platform.
--
-- This file documents the schema for review / ER-diagram purposes.
-- In practice, tables are created and migrated by SQLAlchemy
-- (`db.create_all()` in backend/app/seed.py, or a migration tool such as
-- Flask-Migrate/Alembic in a real production rollout). Keep this file in
-- sync with backend/app/models/*.py when the schema changes.
-- =====================================================================

CREATE TABLE IF NOT EXISTS departments (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(120) NOT NULL UNIQUE,
    annual_budget   DECIMAL(14, 2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS employees (
    id                              INT AUTO_INCREMENT PRIMARY KEY,
    employee_code                   VARCHAR(20) NOT NULL UNIQUE,
    first_name                      VARCHAR(80) NOT NULL,
    last_name                       VARCHAR(80) NOT NULL,
    email                           VARCHAR(255) NOT NULL UNIQUE,
    gender                          VARCHAR(20) DEFAULT 'Undisclosed',
    department_id                   INT NOT NULL,
    job_title                       VARCHAR(120) NOT NULL,
    manager_id                      INT NULL,
    joining_date                    DATE NOT NULL,
    exit_date                       DATE NULL,
    is_active                       BOOLEAN NOT NULL DEFAULT TRUE,
    attrited                        BOOLEAN NOT NULL DEFAULT FALSE,
    exit_reason                     VARCHAR(255) NULL,
    monthly_salary                  DECIMAL(12, 2) NOT NULL,
    last_salary_hike_pct            FLOAT DEFAULT 0,
    promotions_count                INT DEFAULT 0,
    years_since_last_promotion      FLOAT DEFAULT 0,
    performance_score               FLOAT DEFAULT 3.0,
    satisfaction_score              FLOAT DEFAULT 3.0,
    attendance_pct                  FLOAT DEFAULT 95.0,
    overtime_hours_monthly          FLOAT DEFAULT 0,
    leave_days_taken_ytd            INT DEFAULT 0,
    training_hours_ytd              FLOAT DEFAULT 0,
    distance_from_home_km           FLOAT DEFAULT 10.0,
    remote_ratio_pct                FLOAT DEFAULT 0,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (manager_id) REFERENCES employees(id),
    INDEX idx_employees_department (department_id),
    INDEX idx_employees_manager (manager_id)
);

CREATE TABLE IF NOT EXISTS users (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    email                   VARCHAR(255) NOT NULL UNIQUE,
    password_hash           VARCHAR(255) NOT NULL,
    full_name               VARCHAR(150) NOT NULL,
    role                    VARCHAR(30) NOT NULL DEFAULT 'EMPLOYEE',
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    is_email_verified       BOOLEAN NOT NULL DEFAULT FALSE,
    two_factor_enabled      BOOLEAN NOT NULL DEFAULT FALSE,
    two_factor_secret       VARCHAR(64) NULL,
    employee_id             INT NULL,
    created_at              DATETIME,
    last_login_at           DATETIME NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

CREATE TABLE IF NOT EXISTS attendance_records (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    employee_id             INT NOT NULL,
    month                   VARCHAR(7) NOT NULL,
    present_days            INT DEFAULT 0,
    absent_days             INT DEFAULT 0,
    late_arrivals           INT DEFAULT 0,
    work_from_home_days     INT DEFAULT 0,
    overtime_hours          FLOAT DEFAULT 0,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    INDEX idx_attendance_employee (employee_id),
    INDEX idx_attendance_month (month)
);

CREATE TABLE IF NOT EXISTS leave_records (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    employee_id     INT NOT NULL,
    leave_type      VARCHAR(30) NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    status          VARCHAR(20) DEFAULT 'APPROVED',
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    INDEX idx_leave_employee (employee_id)
);

CREATE TABLE IF NOT EXISTS performance_reviews (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    employee_id             INT NOT NULL,
    review_period           VARCHAR(20) NOT NULL,
    kpi_achievement_pct     FLOAT DEFAULT 0,
    rating                  FLOAT DEFAULT 3.0,
    reviewer_comments       TEXT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    INDEX idx_performance_employee (employee_id)
);
