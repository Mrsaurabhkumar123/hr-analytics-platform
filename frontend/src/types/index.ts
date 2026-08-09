export type Role =
  | "SUPER_ADMIN"
  | "HR_ADMIN"
  | "HR_MANAGER"
  | "DEPARTMENT_MANAGER"
  | "TEAM_LEAD"
  | "EMPLOYEE"
  | "AUDITOR";

export interface AuthUser {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  is_active: boolean;
  is_email_verified: boolean;
  two_factor_enabled: boolean;
  employee_id: number | null;
  created_at: string | null;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: AuthUser;
}

export interface ExecutiveKpis {
  total_employees: number;
  active_employees: number;
  attrition_rate_pct: number;
  avg_monthly_salary: number;
  avg_performance_score: number;
  avg_satisfaction_score: number;
  avg_attendance_pct: number;
  open_positions: number;
  avg_recruitment_cost_usd: number;
}

export interface ExecutiveDashboardResponse {
  kpis: ExecutiveKpis;
  hiring_trend: { month: string; hires: number }[];
  department_distribution: { department: string; headcount: number }[];
  generated_at: string;
}

export interface Employee {
  id: number;
  employee_code: string;
  full_name: string;
  email: string;
  gender: string;
  department: string | null;
  department_id: number;
  job_title: string;
  manager: string | null;
  joining_date: string;
  tenure_years: number;
  is_active: boolean;
  attrited: boolean;
  performance_score: number;
  satisfaction_score: number;
  attendance_pct: number;
  promotions_count: number;
  training_hours_ytd: number;
  leave_days_taken_ytd: number;
  monthly_salary?: number;
  last_salary_hike_pct?: number;
  years_since_last_promotion?: number;
  overtime_hours_monthly?: number;
  distance_from_home_km?: number;
  remote_ratio_pct?: number;
  exit_reason?: string | null;
  direct_reports?: Employee[];
}

export interface EmployeeListResponse {
  items: Employee[];
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}

export interface Department {
  id: number;
  name: string;
  annual_budget: number;
  headcount: number;
}

export type RiskCategory = "HIGH RISK" | "MEDIUM RISK" | "LOW RISK";

export interface RiskResult {
  employee_id: number;
  employee_code: string;
  full_name: string;
  department: string | null;
  job_title: string;
  risk_score_pct: number;
  risk_category: RiskCategory;
  reasons: string[];
  suggested_actions: string[];
}

export interface RiskListResponse {
  count: number;
  high_risk_count: number;
  results: RiskResult[];
}

export interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  train_size: number;
  test_size: number;
  feature_importance: Record<string, number>;
}
