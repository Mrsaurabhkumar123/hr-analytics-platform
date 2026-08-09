import { useEffect, useState } from "react";
import { Search, Download, ChevronLeft, ChevronRight, ArrowUpDown } from "lucide-react";
import { employeesApi, departmentsApi } from "../api/client";
import type { Employee, Department } from "../types";
import { PageHeader } from "../components/PageHeader";
import { LoadingState, ErrorState, EmptyState } from "../components/StateViews";

const SORT_OPTIONS: { value: string; label: string }[] = [
  { value: "employee_code", label: "Employee code" },
  { value: "full_name", label: "Name" },
  { value: "department", label: "Department" },
  { value: "performance_score", label: "Performance" },
  { value: "joining_date", label: "Joining date" },
  { value: "monthly_salary", label: "Salary" },
];

export function EmployeeDirectory() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [query, setQuery] = useState("");
  const [departmentId, setDepartmentId] = useState("");
  const [status, setStatus] = useState("");
  const [sortBy, setSortBy] = useState("employee_code");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    departmentsApi.list().then(setDepartments).catch(() => undefined);
  }, []);

  useEffect(() => {
    setLoading(true);
    const timeout = setTimeout(() => {
      employeesApi
        .list({
          page,
          per_page: 12,
          q: query || undefined,
          department_id: departmentId || undefined,
          status: status || undefined,
          sort_by: sortBy,
          sort_dir: sortDir,
        })
        .then((res) => {
          setEmployees(res.items);
          setTotal(res.total);
          setTotalPages(res.total_pages || 1);
          setError(null);
        })
        .catch(() => setError("Could not load the employee directory."))
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timeout);
  }, [page, query, departmentId, status, sortBy, sortDir]);

  function toggleSort(field: string) {
    if (sortBy === field) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(field);
      setSortDir("asc");
    }
  }

  return (
    <div className="p-8">
      <PageHeader
        title="Employee Directory"
        subtitle={`${total.toLocaleString()} employees on record`}
        action={
          <a href={employeesApi.exportCsvUrl()} target="_blank" rel="noreferrer" className="btn-secondary text-sm">
            <Download className="h-4 w-4" /> Export CSV
          </a>
        }
      />

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="relative min-w-[240px] flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-muted" />
          <input
            value={query}
            onChange={(e) => {
              setPage(1);
              setQuery(e.target.value);
            }}
            placeholder="Search name, email, employee code, title..."
            className="input-field pl-9"
          />
        </div>
        <select
          value={departmentId}
          onChange={(e) => {
            setPage(1);
            setDepartmentId(e.target.value);
          }}
          className="input-field w-auto"
        >
          <option value="">All departments</option>
          {departments.map((d) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>
        <select
          value={status}
          onChange={(e) => {
            setPage(1);
            setStatus(e.target.value);
          }}
          className="input-field w-auto"
        >
          <option value="">All statuses</option>
          <option value="active">Active</option>
          <option value="exited">Exited</option>
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="input-field w-auto"
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              Sort: {o.label}
            </option>
          ))}
        </select>
      </div>

      {error && <ErrorState message={error} />}

      {!error && (
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-base-border text-xs uppercase tracking-wide text-ink-muted">
                  <Th label="Employee" field="full_name" sortBy={sortBy} sortDir={sortDir} onClick={toggleSort} />
                  <Th label="Department" field="department" sortBy={sortBy} sortDir={sortDir} onClick={toggleSort} />
                  <th className="px-4 py-3 font-medium">Title</th>
                  <Th label="Joined" field="joining_date" sortBy={sortBy} sortDir={sortDir} onClick={toggleSort} />
                  <Th label="Performance" field="performance_score" sortBy={sortBy} sortDir={sortDir} onClick={toggleSort} />
                  <th className="px-4 py-3 font-medium">Attendance</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={7} className="p-0">
                      <LoadingState />
                    </td>
                  </tr>
                ) : employees.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="p-0">
                      <EmptyState message="No employees match these filters." />
                    </td>
                  </tr>
                ) : (
                  employees.map((e) => (
                    <tr key={e.id} className="border-b border-base-border/60 last:border-0 hover:bg-base-alt/30">
                      <td className="px-4 py-3">
                        <p className="font-medium text-ink-primary">{e.full_name}</p>
                        <p className="text-xs text-ink-muted">{e.employee_code} · {e.email}</p>
                      </td>
                      <td className="px-4 py-3 text-ink-secondary">{e.department}</td>
                      <td className="px-4 py-3 text-ink-secondary">{e.job_title}</td>
                      <td className="px-4 py-3 text-ink-secondary">{e.joining_date}</td>
                      <td className="px-4 py-3 font-mono text-ink-secondary">{e.performance_score.toFixed(1)}</td>
                      <td className="px-4 py-3 font-mono text-ink-secondary">{e.attendance_pct.toFixed(0)}%</td>
                      <td className="px-4 py-3">
                        <span className={e.is_active ? "badge-low" : "badge-high"}>
                          {e.is_active ? "Active" : "Exited"}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between border-t border-base-border px-4 py-3">
            <p className="text-xs text-ink-muted">
              Page {page} of {totalPages}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="btn-secondary px-2.5 py-1.5"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="btn-secondary px-2.5 py-1.5"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Th({
  label,
  field,
  sortBy,
  sortDir,
  onClick,
}: {
  label: string;
  field: string;
  sortBy: string;
  sortDir: "asc" | "desc";
  onClick: (field: string) => void;
}) {
  const active = sortBy === field;
  return (
    <th className="px-4 py-3 font-medium">
      <button onClick={() => onClick(field)} className={`flex items-center gap-1 hover:text-ink-primary ${active ? "text-brand" : ""}`}>
        {label}
        <ArrowUpDown className="h-3 w-3" />
        {active && <span className="text-[10px]">{sortDir === "asc" ? "↑" : "↓"}</span>}
      </button>
    </th>
  );
}
