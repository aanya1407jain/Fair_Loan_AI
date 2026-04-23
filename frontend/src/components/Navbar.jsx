import "./Navbar.css";

export default function Navbar({ page, setPage }) {
  const links = [
    { id: "dashboard", label: "Home" },
    { id: "upload", label: "Upload Model" },
    { id: "report", label: "Audit Report" },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span className="brand-icon">⚖</span>
        <span className="brand-name">Fair<span>Loan</span>AI</span>
        <span className="brand-tag">Bias Auditor</span>
      </div>
      <div className="navbar-links">
        {links.map(l => (
          <button
            key={l.id}
            className={`nav-link ${page === l.id ? "active" : ""}`}
            onClick={() => setPage(l.id)}
          >
            {l.label}
          </button>
        ))}
      </div>
      <div className="navbar-meta">
        <span className="meta-badge">RBI Aligned</span>
      </div>
    </nav>
  );
}
