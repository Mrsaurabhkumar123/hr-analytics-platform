import axios, { AxiosError } from "axios";
import type {
  LoginResponse,
  ExecutiveDashboardResponse,
  EmployeeListResponse,
  Employee,
  Department,
  RiskListResponse,
  ModelMetrics,
  AuthUser,
} from "../types";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

const client = axios.create({ baseURL: BASE_URL });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// On a 401 (expired access token), try one silent refresh using the
// refresh token before giving up and forcing the user back to /login.
let isRefreshing = false;
client.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (typeof error.config & { _retry?: boolean }) | undefined;
    if (error.response?.status === 401 && original && !original._retry && !isRefreshing) {
      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(error);
      }
      original._retry = true;
      isRefreshing = true;
      try {
        const { data } = await axios.post(`${BASE_URL}/auth/refresh`, null, {
          headers: { Authorization: `Bearer ${refreshToken}` },
        });
        localStorage.setItem("access_token", data.access_token);
        isRefreshing = false;
        original.headers = original.headers || {};
        (original.headers as Record<string, string>).Authorization = `Bearer ${data.access_token}`;
        return client(original);
      } catch (refreshError) {
        isRefreshing = false;
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (email: string, password: string) =>
    client.post<LoginResponse>("/auth/login", { email, password }).then((r) => r.data),
  me: () => client.get<AuthUser>("/auth/me").then((r) => r.data),
};

export const dashboardApi = {
  executive: () => client.get<ExecutiveDashboardResponse>("/dashboard/executive").then((r) => r.data),
};

export const employeesApi = {
  list: (params: Record<string, string | number | undefined>) =>
    client.get<EmployeeListResponse>("/employees", { params }).then((r) => r.data),
  get: (id: number) => client.get<Employee>(`/employees/${id}`).then((r) => r.data),
  exportCsvUrl: () => `${BASE_URL}/employees/export`,
};

export const departmentsApi = {
  list: () => client.get<Department[]>("/departments").then((r) => r.data),
};

export const attritionApi = {
  risk: () => client.get<RiskListResponse>("/attrition/risk").then((r) => r.data),
  employeeRisk: (id: number) => client.get(`/attrition/risk/${id}`).then((r) => r.data),
  modelMetrics: () => client.get<ModelMetrics>("/attrition/model/metrics").then((r) => r.data),
  trend: () => client.get("/attrition/trend").then((r) => r.data),
  heatmap: () => client.get("/attrition/heatmap").then((r) => r.data),
};

export default client;
