"""
Bias Audit Engine
Computes fairness metrics: Disparate Impact (DI), Equal Opportunity (EO),
Demographic Parity (DP) across demographic groups.
Compatible with Fairlearn and AIF360.
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import json
import warnings
warnings.filterwarnings("ignore")


# ── Fairness metric functions ──────────────────────────────────────────────

def disparate_impact_ratio(y_pred: np.ndarray, sensitive: np.ndarray,
                            privileged_val: str) -> Dict:
    """
    DI = P(Ŷ=1 | unprivileged) / P(Ŷ=1 | privileged)
    A value < 0.8 indicates disparate impact (4/5 rule).
    """
    results = {}
    groups = np.unique(sensitive)
    priv_mask = sensitive == privileged_val
    priv_rate = y_pred[priv_mask].mean() if priv_mask.sum() > 0 else 0.0001

    for g in groups:
        mask = sensitive == g
        if mask.sum() < 10:
            continue
        group_rate = y_pred[mask].mean()
        di = group_rate / priv_rate if priv_rate > 0 else 0
        results[str(g)] = {
            "approval_rate": round(float(group_rate), 4),
            "di_ratio": round(float(di), 4),
            "count": int(mask.sum()),
            "approved": int(y_pred[mask].sum()),
            "flagged": di < 0.8 and str(g) != privileged_val
        }
    return results


def equal_opportunity_difference(y_true: np.ndarray, y_pred: np.ndarray,
                                   sensitive: np.ndarray, privileged_val: str) -> Dict:
    """
    EOD = TPR(unprivileged) - TPR(privileged)
    Measures if qualified applicants get equal approval rates.
    """
    results = {}
    priv_mask = (sensitive == privileged_val) & (y_true == 1)
    priv_tpr = y_pred[priv_mask].mean() if priv_mask.sum() > 0 else 0

    for g in np.unique(sensitive):
        mask = (sensitive == g) & (y_true == 1)
        if mask.sum() < 5:
            continue
        group_tpr = y_pred[mask].mean() if mask.sum() > 0 else 0
        eod = group_tpr - priv_tpr
        results[str(g)] = {
            "true_positive_rate": round(float(group_tpr), 4),
            "eod": round(float(eod), 4),
            "qualified_count": int(mask.sum()),
            "flagged": abs(eod) > 0.1 and str(g) != privileged_val
        }
    return results


def demographic_parity_difference(y_pred: np.ndarray, sensitive: np.ndarray,
                                   privileged_val: str) -> Dict:
    """
    DPD = P(Ŷ=1 | unprivileged) - P(Ŷ=1 | privileged)
    """
    results = {}
    priv_mask = sensitive == privileged_val
    priv_rate = y_pred[priv_mask].mean() if priv_mask.sum() > 0 else 0

    for g in np.unique(sensitive):
        mask = sensitive == g
        if mask.sum() < 10:
            continue
        group_rate = y_pred[mask].mean()
        dpd = group_rate - priv_rate
        results[str(g)] = {
            "approval_rate": round(float(group_rate), 4),
            "dpd": round(float(dpd), 4),
            "flagged": abs(dpd) > 0.05 and str(g) != privileged_val
        }
    return results


def compute_overall_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
    """Standard ML metrics."""
    tp = ((y_pred == 1) & (y_true == 1)).sum()
    tn = ((y_pred == 0) & (y_true == 0)).sum()
    fp = ((y_pred == 1) & (y_true == 0)).sum()
    fn = ((y_pred == 0) & (y_true == 1)).sum()

    accuracy = (tp + tn) / len(y_true)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "approval_rate": round(float(y_pred.mean()), 4),
        "total_samples": int(len(y_true)),
        "total_approved": int(y_pred.sum()),
        "total_rejected": int((y_pred == 0).sum())
    }


def score_severity(di_results: Dict, sensitive_attr: str) -> str:
    """Compute overall bias severity for a sensitive attribute."""
    flagged = [v for v in di_results.values() if v.get("flagged", False)]
    if len(flagged) == 0:
        return "PASS"
    worst_di = min(v["di_ratio"] for v in di_results.values())
    if worst_di < 0.6:
        return "CRITICAL"
    elif worst_di < 0.7:
        return "HIGH"
    elif worst_di < 0.8:
        return "MEDIUM"
    return "LOW"


# ── Main audit function ────────────────────────────────────────────────────

def run_audit(df: pd.DataFrame, model=None, model_type: str = "demo") -> Dict[str, Any]:
    """
    Run full bias audit on a dataframe.
    Returns a comprehensive bias report JSON.
    """
    audit_id = str(uuid.uuid4())[:8].upper()
    timestamp = datetime.utcnow().isoformat()

    y_true = df["fair_approved"].values
    y_pred = df["model_approved"].values

    # ── Overall model metrics ──────────────────────────────────────
    overall = compute_overall_metrics(y_true, y_pred)

    # ── Sensitive attribute audits ─────────────────────────────────
    sensitive_attrs = {
        "gender":       {"col": "gender",      "privileged": "Male"},
        "city_tier":    {"col": "city_tier",   "privileged": 1},
        "religion":     {"col": "religion",    "privileged": "Hindu"},
    }

    bias_results = {}

    for attr_name, cfg in sensitive_attrs.items():
        col = cfg["col"]
        priv = cfg["privileged"]
        sensitive = df[col].values

        di = disparate_impact_ratio(y_pred, sensitive, priv)
        eod = equal_opportunity_difference(y_true, y_pred, sensitive, priv)
        dpd = demographic_parity_difference(y_pred, sensitive, priv)
        severity = score_severity(di, attr_name)

        bias_results[attr_name] = {
            "privileged_group": str(priv),
            "severity": severity,
            "disparate_impact": di,
            "equal_opportunity": eod,
            "demographic_parity": dpd,
            "summary": _generate_summary(attr_name, severity, di, priv)
        }

    # ── Intersectional analysis ────────────────────────────────────
    intersectional = _intersectional_analysis(df, y_pred)

    # ── Mitigation suggestions ─────────────────────────────────────
    mitigations = _generate_mitigations(bias_results)

    # ── Risk score (0-100) ─────────────────────────────────────────
    risk_score = _compute_risk_score(bias_results)

    report = {
        "audit_id": audit_id,
        "timestamp": timestamp,
        "model_type": model_type,
        "dataset": {
            "total_samples": int(len(df)),
            "features": list(df.columns),
            "source": "synthetic_indian_demographics"
        },
        "overall_metrics": overall,
        "bias_analysis": bias_results,
        "intersectional": intersectional,
        "risk_score": risk_score,
        "risk_level": _risk_level(risk_score),
        "mitigation_suggestions": mitigations,
        "regulatory_notes": _regulatory_notes(bias_results),
        "rbi_compliant": bool(risk_score < 40)
    }

    return _sanitize(report)


def _generate_summary(attr: str, severity: str, di: Dict, priv: Any) -> str:
    """Human-readable summary for each attribute."""
    flagged = [g for g, v in di.items() if v.get("flagged")]
    if not flagged:
        return f"No significant bias detected for {attr}."
    groups_str = ", ".join(flagged)
    return (
        f"{severity} bias detected for {attr}. "
        f"Groups {groups_str} face significantly lower approval rates "
        f"compared to {priv}."
    )


def _intersectional_analysis(df: pd.DataFrame, y_pred: np.ndarray) -> list:
    """Cross-group analysis for intersecting protected attributes."""
    results = []
    df = df.copy()
    df["_pred"] = y_pred

    for gender in ["Male", "Female"]:
        for tier in [1, 2, 3]:
            mask = (df["gender"] == gender) & (df["city_tier"] == tier)
            if mask.sum() < 20:
                continue
            rate = df.loc[mask, "_pred"].mean()
            results.append({
                "gender": gender,
                "city_tier": tier,
                "approval_rate": round(float(rate), 4),
                "count": int(mask.sum())
            })

    return results


def _generate_mitigations(bias_results: Dict) -> list:
    """Suggest mitigation strategies based on detected biases."""
    suggestions = []

    for attr, data in bias_results.items():
        if data["severity"] in ("CRITICAL", "HIGH"):
            suggestions.append({
                "attribute": attr,
                "technique": "Reweighting",
                "description": f"Apply sample reweighting to up-weight underrepresented {attr} groups during training.",
                "fairlearn_api": "fairlearn.reductions.ExponentiatedGradient",
                "priority": "HIGH"
            })
            suggestions.append({
                "attribute": attr,
                "technique": "Threshold Optimization",
                "description": f"Use group-specific decision thresholds to equalize approval rates across {attr}.",
                "fairlearn_api": "fairlearn.postprocessing.ThresholdOptimizer",
                "priority": "HIGH"
            })
        elif data["severity"] == "MEDIUM":
            suggestions.append({
                "attribute": attr,
                "technique": "Calibrated Equalized Odds",
                "description": f"Post-process predictions to satisfy equalized odds for {attr}.",
                "fairlearn_api": "fairlearn.postprocessing.ThresholdOptimizer(constraints='equalized_odds')",
                "priority": "MEDIUM"
            })

    if not suggestions:
        suggestions.append({
            "attribute": "all",
            "technique": "Continuous Monitoring",
            "description": "No critical biases detected. Implement ongoing monitoring with quarterly audits.",
            "priority": "LOW"
        })

    return suggestions


def _compute_risk_score(bias_results: Dict) -> int:
    severity_map = {"CRITICAL": 40, "HIGH": 25, "MEDIUM": 15, "LOW": 5, "PASS": 0}
    score = sum(severity_map.get(v["severity"], 0) for v in bias_results.values())
    return min(100, score)

def _risk_level(score: int) -> str:
    if score >= 70: return "CRITICAL"
    if score >= 50: return "HIGH"
    if score >= 30: return "MEDIUM"
    if score >= 10: return "LOW"
    return "MINIMAL"

def _sanitize(obj):
    """Recursively convert numpy types to native Python types for JSON serialization."""
    import numpy as np
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize(i) for i in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj



    if score >= 70: return "CRITICAL"
    if score >= 50: return "HIGH"
    if score >= 30: return "MEDIUM"
    if score >= 10: return "LOW"
    return "MINIMAL"


def _regulatory_notes(bias_results: Dict) -> list:
    notes = [
        "This audit follows RBI's Fair Lending Practices guidelines (Master Circular 2023).",
        "Disparate Impact threshold of 0.8 per the 4/5ths rule (US EEOC standard, adopted as best practice).",
    ]
    critical = [a for a, v in bias_results.items() if v["severity"] == "CRITICAL"]
    if critical:
        notes.append(
            f"CRITICAL: Attributes {critical} show significant disparate impact. "
            "Immediate remediation required before production deployment."
        )
    return notes