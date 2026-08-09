import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ProtectedShell } from "./components/AppShell";
import { Login } from "./pages/Login";
import { ExecutiveDashboard } from "./pages/ExecutiveDashboard";
import { EmployeeDirectory } from "./pages/EmployeeDirectory";
import { AttritionRisk } from "./pages/AttritionRisk";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedShell />}>
            <Route path="/" element={<ExecutiveDashboard />} />
            <Route path="/employees" element={<EmployeeDirectory />} />
            <Route path="/attrition-risk" element={<AttritionRisk />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
