import "./Dashboard.css";

export default function Dashboard({ onRunDemo, loading }) {
  return (
    <div className="dashboard">
      <div className="hero">
        <div className="hero-badge">India's Credit Fairness Layer</div>
        <h1 className="hero-title">
          Detect Bias in<br />
          <span>Loan Scoring Models</span>
        </h1>
        <p className="hero-desc">
          Banks and NBFCs use ML models to approve or reject loans — often encoding
          historical discrimination against gender, religion, or geography.
          Fair Loan AI audits any model for disparate impact and generates
          RBI-ready compliance reports.
        </p>
        <div className="hero-actions">
          <button className="btn-primary" onClick={onRunDemo} disabled={loading}>
            {loading ? "Running Audit…" : "▶  Run Demo Audit"}
          </button>
          <button className="btn-secondary" onClick={() => {}}>
            ↑  Upload Your Model
          </button>
        </div>
      </div>

      <div className="features-grid">
        {FEATURES.map(f => (
          <div key={f.title} className="feature-card">
            <div className="feature-icon">{f.icon}</div>
            <div className="feature-title">{f.title}</div>
            <div className="feature-desc">{f.desc}</div>
          </div>
        ))}
      </div>

      <div className="metrics-strip">
        {METRICS.map(m => (
          <div key={m.label} className="metric-item">
            <div className="metric-val">{m.val}</div>
            <div className="metric-label">{m.label}</div>
          </div>
        ))}
      </div>

      <div className="flow-section">
        <h2>How It Works</h2>
        <div className="flow-steps">
          {STEPS.map((s, i) => (
            <div key={i} className="flow-step">
              <div className="step-num">{String(i + 1).padStart(2, "0")}</div>
              <div className="step-title">{s.title}</div>
              <div className="step-desc">{s.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const FEATURES = [
  { icon: "🔍", title: "Disparate Impact Analysis", desc: "Computes DI ratios across gender, religion, city tier. Flags violations of the 4/5 rule." },
  { icon: "⚖", title: "Equal Opportunity Audit", desc: "Measures if qualified applicants from all groups get equal approval rates." },
  { icon: "🗺", title: "Bias Heatmap", desc: "Interactive group × metric grid showing exactly where discrimination is occurring." },
  { icon: "🛠", title: "Mitigation Suggestions", desc: "Recommends Fairlearn/AIF360 techniques: reweighting, threshold optimization." },
  { icon: "📄", title: "Regulator PDF Export", desc: "One-click PDF reports formatted for RBI submission and compliance review." },
  { icon: "📊", title: "Synthetic Indian Data", desc: "5,000-sample synthetic dataset with realistic Indian demographics for testing." },
];

const METRICS = [
  { val: "3", label: "Fairness Metrics" },
  { val: "5K+", label: "Sample Dataset" },
  { val: "RBI", label: "Aligned" },
  { val: "PDF", label: "Report Export" },
  { val: "Free", label: "Open Source" },
];

const STEPS = [
  { title: "Load Data", desc: "Use our synthetic Indian demographic dataset or plug in your own RBI/Kaggle data." },
  { title: "Run Model", desc: "Upload a .pkl credit scoring model (XGBoost, LogReg, etc.) or use our built-in demo." },
  { title: "Compute Metrics", desc: "Fairlearn computes DI, EO, and DP ratios across gender, religion, and city tier." },
  { title: "Review Heatmap", desc: "See which groups face bias — visualized in an interactive bias heatmap grid." },
  { title: "Export Report", desc: "Download a PDF bias audit report, ready to hand to RBI regulators." },
];
