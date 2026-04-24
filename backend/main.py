"""
Fair Loan AI — FastAPI Audit Engine
Bias auditing for credit scoring models using Fairlearn / AIF360
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import json
import os
import pickle
import tempfile
from pathlib import Path

from audit_engine import run_audit
from data_generator import generate_synthetic_data
from report_generator import generate_pdf_report

app = FastAPI()

# ADD THIS BLOCK
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://fair-loan-ai.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... rest of your existing routes below

app = FastAPI(
    title="Fair Loan AI — Bias Audit Engine",
    description="Credit scoring bias auditor for Indian banking models",
    version="1.0.0"
)

REPORTS_DIR = Path("./reports")
REPORTS_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {"message": "Fair Loan AI Audit Engine running", "version": "1.0.0"}


@app.get("/api/demo-audit")
def demo_audit():
    """Run a demo audit using synthetic data + built-in model."""
    df = generate_synthetic_data(n_samples=5000, seed=42)
    report = run_audit(df, model_type="demo")
    return report


@app.post("/api/upload-model")
async def upload_model(file: UploadFile = File(...)):
    """Upload a .pkl model file and audit it against synthetic data."""
    if not file.filename.endswith(".pkl"):
        raise HTTPException(status_code=400, detail="Only .pkl files supported")

    contents = await file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            model = pickle.load(f)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load model: {str(e)}")
    finally:
        os.unlink(tmp_path)

    df = generate_synthetic_data(n_samples=5000, seed=42)
    report = run_audit(df, model=model, model_type="uploaded")
    return report


@app.post("/api/audit-json")
async def audit_json(payload: dict):
    """Run audit with custom parameters."""
    n_samples = payload.get("n_samples", 5000)
    seed = payload.get("seed", 42)
    df = generate_synthetic_data(n_samples=n_samples, seed=seed)
    report = run_audit(df, model_type="demo")
    return report


@app.get("/api/export-pdf/{audit_id}")
def export_pdf(audit_id: str):
    """Export audit report as PDF for regulators."""
    report_path = REPORTS_DIR / f"{audit_id}.json"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Audit report not found")

    with open(report_path) as f:
        report = json.load(f)

    pdf_path = generate_pdf_report(report, audit_id)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"bias_audit_report_{audit_id}.pdf"
    )


@app.get("/api/save-report/{audit_id}")
def save_report(audit_id: str, report: dict):
    path = REPORTS_DIR / f"{audit_id}.json"
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    return {"saved": True, "path": str(path)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
