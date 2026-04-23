import { useState, useEffect } from "react";
import Dashboard from "./pages/Dashboard";
import UploadPage from "./pages/UploadPage";
import ReportPage from "./pages/ReportPage";
import Navbar from "./components/Navbar";
import "./App.css";

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [auditReport, setAuditReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const runDemoAudit = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/demo-audit");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setAuditReport(data);
      setPage("report");
    } catch (e) {
      alert("Backend not running or unreachable.\n\nFix:\n1. Open a new terminal\n2. cd backend\n3. pip install -r requirements.txt\n4. uvicorn main:app --reload\n\nThen try again.");
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