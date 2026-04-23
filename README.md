# ⚖ Fair Loan AI — Credit Scoring Bias Auditor

**A bias audit tool for loan approval ML models, aligned with RBI fair lending guidelines.**

Detects disparate impact across gender, religion, and geography in Indian credit scoring models. Generates regulator-ready PDF reports.

---

## 🗂 Project Structure

```
fair-loan-ai/
├── backend/
│   ├── main.py                 # FastAPI server (audit engine API)
│   ├── audit_engine.py         # Core bias metrics: DI, EO, DP
│   ├── data_generator.py       # Synthetic Indian demographic data
│   ├── report_generator.py     # PDF report export
│   ├── train_demo_model.py     # Train a demo biased model
│   ├── run_audit.py            # CLI audit tool (no server needed)
│   ├── requirements.txt
│   └── models/                 # Saved .pkl models go here
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   └── BiasHeatmap.jsx # Interactive bias heatmap
│   │   └── pages/
│   │       ├── Dashboard.jsx   # Landing page
│   │       ├── UploadPage.jsx  # Model upload
│   │       └── ReportPage.jsx  # Audit results
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## 🚀 Quick Start

### Option A: CLI Only (fastest, no frontend needed)

```bash
cd backend
pip install -r requirements.txt
python run_audit.py                        # demo audit with synthetic data
python run_audit.py --output report.json   # save report
python run_audit.py --model models/my.pkl  # audit your own model
```

### Option B: Full Stack (backend + React dashboard)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API runs at http://localhost:8000
# Docs at http://localhost:8000/docs
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:3000
```

---

## 📊 Fairness Metrics Explained

| Metric | Formula | Threshold |
|--------|---------|-----------|
| **Disparate Impact (DI)** | P(approved \| unprivileged) / P(approved \| privileged) | < 0.8 = bias (4/5 rule) |
| **Equal Opportunity Diff (EOD)** | TPR(unprivileged) − TPR(privileged) | > 0.1 = concern |
| **Demographic Parity Diff (DPD)** | P(approved \| group) − P(approved \| reference) | > 0.05 = concern |

### Protected Attributes Audited
- **Gender** — Male / Female / Other (reference: Male)
- **Religion** — Hindu / Muslim / Christian / Sikh / etc. (reference: Hindu)  
- **City Tier** — Tier 1 (metros) / Tier 2 / Tier 3 (reference: Tier 1)

---

## 🛠 Mitigation Techniques

The tool recommends specific Fairlearn strategies:

```python
# Reweighting (pre-processing)
from fairlearn.reductions import ExponentiatedGradient, DemographicParity
mitigator = ExponentiatedGradient(estimator, DemographicParity())
mitigator.fit(X_train, y_train, sensitive_features=A_train)

# Threshold optimization (post-processing)
from fairlearn.postprocessing import ThresholdOptimizer
postproc = ThresholdOptimizer(estimator=model, constraints="equalized_odds")
postproc.fit(X_train, y_train, sensitive_features=A_train)
```

---

## 📄 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/demo-audit` | GET | Run audit with synthetic data + demo model |
| `POST /api/upload-model` | POST | Upload .pkl model for auditing |
| `GET /api/export-pdf/{audit_id}` | GET | Download PDF report |
| `GET /docs` | GET | Interactive Swagger API docs |

---

## 🏗 Train a Demo Model

```bash
cd backend
python train_demo_model.py
# Creates: models/demo_model.pkl (a biased GradientBoosting model)
# Upload via dashboard or CLI to test the audit
```

---

## 📋 Sample Bias Report Output

```
══════════════════════════════════════════════════════════
  Fair Loan AI — Bias Audit Report
══════════════════════════════════════════════════════════
  Audit ID  : 4A2F7B1C
  Risk Score: 65/100  (HIGH)
  RBI Compliant: ✗ NO

  [CRITICAL] GENDER
  Female applicants face 23% lower approval rate (DI: 0.71)

  [HIGH] RELIGION
  Muslim applicants face 18% lower approval rate (DI: 0.76)

  [HIGH] CITY_TIER
  Tier 3 city applicants face 21% lower approval rate (DI: 0.73)

  Mitigation: Fairlearn ThresholdOptimizer (equalized_odds)
══════════════════════════════════════════════════════════
```

---

## 🏛 Regulatory Context

- **RBI Master Circular on Fair Lending Practices** (2023)
- **SEBI AI/ML Model Risk Management Guidelines**
- **EU AI Act** — high-risk AI system (credit scoring) compliance
- **US EEOC 4/5 Rule** — adopted as DI threshold best practice

---

## 📦 Dependencies

**Backend:**
- `fastapi` — API server
- `fairlearn` — fairness metrics and mitigation
- `aif360` — IBM AI Fairness 360 toolkit
- `scikit-learn` — ML pipeline
- `numpy`, `pandas` — data processing
- `reportlab` — PDF generation

**Frontend:**
- `react` 18 — UI framework
- `vite` — build tool

---

## 🏆 Why This Matters

India has 190M+ credit-underserved adults. ML-driven loan rejection without fairness audits perpetuates historical discrimination against women, minorities, and rural applicants. This tool gives banks, NBFCs, and regulators a concrete way to measure and fix algorithmic bias.

---

*Built for Hackathons · Aligned with RBI Fair Lending · Open Source*
