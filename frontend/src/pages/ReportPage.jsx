import BiasHeatmap from "../components/BiasHeatmap";
import "./ReportPage.css";

const RISK_COLORS = {
  CRITICAL: "#ff6b6b",
  HIGH: "#ffd166",
  MEDIUM: "#f4a261",
  LOW: "#06d6a0",
  MINIMAL: "#06d6a0",
};

export default function ReportPage({ report }) {
  if (!report) return null;

  const riskColor = RISK_COLORS[report.risk_level] || "#64748b";

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `bias_audit_${report.audit_id}.json`;
    a.click();
  };

  return (
    <div className="report-page">
      {/* Header */}
      <div className="report-header">
        <div className="report-meta">
          <div className="report-id">AUDIT #{report.audit_id}</div>
          <div className="report-date">{report.timestamp?.slice(0, 10)} — {report.dataset?.total_samples?.toLocaleString()} samples</div>
        </div>
        <button className="export-btn" onClick={handleExport}>↓ Export JSON</button>
      </div>

      {/* Risk Score Banner */}
      <div className="risk-banner" style={{ borderColor: riskColor }}>
        <div className="risk-score-wrap">
          <div className="risk-score" style={{ color: riskColor }}>{report.risk_score}</div>
          <div className="risk-score-label">/ 100</div>
        </div>
        <div className="risk-details">
          <div className="risk-level" style={{ color: riskColor }}>{report.risk_level} RISK</div>
          <div className="rbi-status">
            RBI Compliant:
            <span style={{ color: report.rbi_compliant ? "#06d6a0" : "#ff6b6b" }}>
              {report.rbi_compliant ? " ✓ YES" : " ✗ NO"}
            </span>
          </div>
        </div>
        <div className="risk-gauge">
          <div className="gauge-bar">
            <div className="gauge-fill" style={{ width: `${report.risk_score}%`, background: riskColor }}></div>
          </div>
          <div className="gauge-labels">
            <span>PASS</span><span>LOW</span><span>MED</span><span>HIGH</span><span>CRIT</span>
          </div>
        </div>
      </div>

      {/* Overall Metrics */}
      <div className="section">
        <h2 className="section-title">Model Performance</h2>
        <div className="metrics-grid">
          {Object.entries(report.overall_metrics || {}).slice(0, 6).map(([k, v]) => (
            <div key={k} className="metric-card">
              <div className="mc-label">{k.replace(/_/g, " ").toUpperCase()}</div>
              <div className="mc-val">
                {typeof v === "number" && v <= 1 && k !== "total_samples" && k !== "total_approved" && k !== "total_rejected"
                  ? (v * 100).toFixed(1) + "%"
                  : v.toLocaleString()
                }
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bias Heatmap */}
      <div className="section">
        <h2 className="section-title">Bias Analysis</h2>
        <BiasHeatmap biasAnalysis={report.bias_analysis} />
      </div>

      {/* Intersectional */}
      <div className="section">
        <h2 className="section-title">Intersectional Analysis</h2>
        <div className="intersect-grid">
          {(report.intersectional || []).map((row, i) => (
            <div key={i} className="intersect-card">
              <div className="ic-label">{row.gender} · Tier {row.city_tier}</div>
              <div className="ic-bar-wrap">
                <div className="ic-bar" style={{ width: `${row.approval_rate * 100}%` }}></div>
                <span className="ic-val">{(row.approval_rate * 100).toFixed(1)}%</span>
              </div>
              <div className="ic-count">n={row.count}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Mitigations */}
      <div className="section">
        <h2 className="section-title">Mitigation Suggestions</h2>
        <div className="mitigations">
          {(report.mitigation_suggestions || []).map((m, i) => (
            <div key={i} className={`mitigation-card priority-${m.priority.toLowerCase()}`}>
              <div className="mit-header">
                <span className="mit-priority">{m.priority}</span>
                <span className="mit-technique">{m.technique}</span>
                <span className="mit-attr">{m.attribute}</span>
              </div>
              <div className="mit-desc">{m.description}</div>
              {m.fairlearn_api && (
                <div className="mit-api">
                  <span>API: </span><code>{m.fairlearn_api}</code>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Regulatory Notes */}
      <div className="section">
        <h2 className="section-title">Regulatory Notes</h2>
        <div className="reg-notes">
          {(report.regulatory_notes || []).map((note, i) => (
            <div key={i} className="reg-note">{note}</div>
          ))}
        </div>
      </div>
    </div>
  );
}
