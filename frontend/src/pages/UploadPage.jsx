import { useState, useRef } from "react";
import "./UploadPage.css";

export default function UploadPage({ setAuditReport, setPage }) {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef();

  const handleFile = (f) => {
    if (!f.name.endsWith(".pkl")) {
      setError("Only .pkl (pickle) model files are supported.");
      return;
    }
    setFile(f);
    setError(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      // ✅ New — uses environment variable
      const API_URL = import.meta.env.VITE_API_URL;
      const res = await fetch(`${API_URL}/api/upload-model`, {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
      }
      const data = await res.json();
      setAuditReport(data);
      setPage("report");
    } catch (e) {
      setError(e.message || "Upload failed. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="upload-container">
        <h1 className="upload-title">Upload Your Model</h1>
        <p className="upload-subtitle">
          Drop a scikit-learn compatible .pkl file. We'll run it against 5,000 synthetic
          Indian loan applicants and compute fairness metrics.
        </p>

        <div
          className={`drop-zone ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pkl"
            style={{ display: "none" }}
            onChange={(e) => e.target.files[0] && handleFile(e.target.files[0])}
          />
          {file ? (
            <div className="file-info">
              <div className="file-icon">📦</div>
              <div className="file-name">{file.name}</div>
              <div className="file-size">{(file.size / 1024).toFixed(1)} KB</div>
            </div>
          ) : (
            <div className="drop-content">
              <div className="drop-icon">⬆</div>
              <div className="drop-text">Drag & drop your .pkl model</div>
              <div className="drop-sub">or click to browse</div>
            </div>
          )}
        </div>

        {error && <div className="upload-error">⚠ {error}</div>}

        <div className="upload-actions">
          <button
            className="btn-upload"
            onClick={handleUpload}
            disabled={!file || loading}
          >
            {loading ? "Auditing…" : "Run Bias Audit"}
          </button>
        </div>

        <div className="model-compat">
          <div className="compat-title">Compatible Models</div>
          <div className="compat-list">
            {["XGBoost", "LightGBM", "LogisticRegression", "RandomForest", "SVC", "Any sklearn model"].map(m => (
              <span key={m} className="compat-tag">{m}</span>
            ))}
          </div>
        </div>

        <div className="model-requirements">
          <div className="req-title">Requirements</div>
          <ul>
            <li>Model must have a <code>predict(X)</code> or <code>predict_proba(X)</code> method</li>
            <li>Input features: cibil_score, monthly_income, loan_amount, debt_to_income_ratio, existing_loans, credit_history_years, num_late_payments</li>
            <li>Output: binary (0/1) approval decision</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
