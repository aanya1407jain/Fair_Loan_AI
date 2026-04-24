import { useState } from "react";
import Dashboard from "./pages/Dashboard";
import UploadPage from "./pages/UploadPage";
import ReportPage from "./pages/ReportPage";
import Navbar from "./components/Navbar";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;  // ← define once at top

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [auditReport, setAuditReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const runDemoAudit = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/demo-audit`, {  // ✅ both backticks
        method: "POST",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setAuditReport(data);
      setPage("report");
    } catch (e) {
      alert("Backend unreachable. Check your VITE_API_URL environment variable.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <Navbar page={page} setPage={setPage} />
      {page === "dashboard" && (
        <Dashboard onRunDemo={runDemoAudit} loading={loading} />
      )}
      {page === "upload" && (
        <UploadPage setAuditReport={setAuditReport} setPage={setPage} />
      )}
      {page === "report" && auditReport && (
        <ReportPage report={auditReport} />
      )}
      {page === "report" && !auditReport && (
        <div className="empty-state">
          <p>No audit report yet. Run a demo audit or upload a model.</p>
          <button onClick={() => setPage("dashboard")}>Go to Dashboard</button>
        </div>
      )}
    </div>
  );
}
