"""
PDF Report Generator
Generates regulator-ready PDF bias audit reports.
Uses ReportLab (free, no external dependencies).
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json

REPORTS_DIR = Path("./reports")
REPORTS_DIR.mkdir(exist_ok=True)


def generate_pdf_report(report: Dict[str, Any], audit_id: str) -> str:
    """
    Generate a PDF report. Uses ReportLab if available, falls back to HTML-as-PDF.
    Returns path to the generated file.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, PageBreak
        )
        return _generate_reportlab_pdf(report, audit_id)
    except ImportError:
        return _generate_html_report(report, audit_id)


def _generate_reportlab_pdf(report: Dict, audit_id: str) -> str:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

    pdf_path = str(REPORTS_DIR / f"{audit_id}.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#1a1a2e"))
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#16213e"))
    body_style = styles["Normal"]

    story = []

    # Header
    story.append(Paragraph("Fair Loan AI — Bias Audit Report", title_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(f"Audit ID: {report['audit_id']} | Date: {report['timestamp'][:10]}", body_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#e94560")))
    story.append(Spacer(1, 0.5*cm))

    # Risk Score
    risk = report.get("risk_score", 0)
    risk_level = report.get("risk_level", "UNKNOWN")
    story.append(Paragraph(f"Overall Risk Score: {risk}/100 ({risk_level})", heading_style))
    story.append(Paragraph(f"RBI Compliant: {'YES' if report.get('rbi_compliant') else 'NO'}", body_style))
    story.append(Spacer(1, 0.5*cm))

    # Overall metrics
    story.append(Paragraph("Model Performance Metrics", heading_style))
    om = report.get("overall_metrics", {})
    metrics_data = [["Metric", "Value"]] + [[k.replace("_", " ").title(), str(v)] for k, v in om.items()]
    t = Table(metrics_data, colWidths=[8*cm, 6*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16213e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # Bias analysis per attribute
    story.append(Paragraph("Bias Analysis by Sensitive Attribute", heading_style))
    for attr, data in report.get("bias_analysis", {}).items():
        severity = data.get("severity", "UNKNOWN")
        color = "#e94560" if severity == "CRITICAL" else "#f5a623" if severity == "HIGH" else "#7ec8e3"
        story.append(Paragraph(
            f"<font color='{color}'>{attr.upper()} — {severity}</font>",
            ParagraphStyle("AttrHead", parent=styles["Heading3"], fontSize=12)
        ))
        story.append(Paragraph(data.get("summary", ""), body_style))
        story.append(Spacer(1, 0.3*cm))

        # DI table
        di = data.get("disparate_impact", {})
        if di:
            di_data = [["Group", "Approval Rate", "DI Ratio", "Status"]]
            for g, v in di.items():
                status = "⚠ FLAGGED" if v.get("flagged") else "✓ OK"
                di_data.append([g, f"{v['approval_rate']:.2%}", f"{v['di_ratio']:.3f}", status])
            t2 = Table(di_data, colWidths=[5*cm, 4*cm, 4*cm, 4*cm])
            t2.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]))
            story.append(t2)
            story.append(Spacer(1, 0.4*cm))

    # Mitigation
    story.append(Paragraph("Mitigation Suggestions", heading_style))
    for m in report.get("mitigation_suggestions", []):
        story.append(Paragraph(f"• [{m['priority']}] {m['technique']}: {m['description']}", body_style))
        story.append(Spacer(1, 0.2*cm))

    # Regulatory notes
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Regulatory Notes", heading_style))
    for note in report.get("regulatory_notes", []):
        story.append(Paragraph(f"• {note}", body_style))

    doc.build(story)
    return pdf_path


def _generate_html_report(report: Dict, audit_id: str) -> str:
    """Fallback: generate an HTML file when ReportLab is unavailable."""
    html_path = str(REPORTS_DIR / f"{audit_id}.html")

    html = f"""<!DOCTYPE html>
<html>
<head><title>Bias Audit Report {audit_id}</title>
<style>
body {{ font-family: Arial, sans-serif; max-width: 900px; margin: auto; padding: 40px; }}
h1 {{ color: #1a1a2e; }} h2 {{ color: #16213e; border-bottom: 2px solid #e94560; }}
table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
th {{ background: #16213e; color: white; padding: 8px; }}
td {{ padding: 8px; border: 1px solid #ddd; }}
.critical {{ color: #e94560; font-weight: bold; }}
.high {{ color: #f5a623; font-weight: bold; }}
.pass {{ color: #2ecc71; }}
</style></head>
<body>
<h1>Fair Loan AI — Bias Audit Report</h1>
<p>Audit ID: <strong>{report['audit_id']}</strong> | Date: {report['timestamp'][:10]}</p>
<p>Risk Score: <strong>{report.get('risk_score',0)}/100</strong> ({report.get('risk_level','')}) |
RBI Compliant: <strong>{'YES' if report.get('rbi_compliant') else 'NO'}</strong></p>

<h2>Model Metrics</h2>
<table><tr><th>Metric</th><th>Value</th></tr>
{''.join(f"<tr><td>{k.replace('_',' ').title()}</td><td>{v}</td></tr>" for k,v in report.get('overall_metrics',{}).items())}
</table>

<h2>Bias Analysis</h2>
{''.join(f"<h3>{attr.upper()} — <span class='{data.get('severity','').lower()}'>{data.get('severity')}</span></h3><p>{data.get('summary','')}</p>" for attr,data in report.get('bias_analysis',{}).items())}

<h2>Mitigation Suggestions</h2>
<ul>{''.join(f"<li><strong>[{m['priority']}] {m['technique']}</strong>: {m['description']}</li>" for m in report.get('mitigation_suggestions',[]))}</ul>

<h2>Regulatory Notes</h2>
<ul>{''.join(f"<li>{n}</li>" for n in report.get('regulatory_notes',[]))}</ul>

<p><em>Generated by Fair Loan AI — {datetime.utcnow().isoformat()}</em></p>
</body></html>"""

    with open(html_path, "w") as f:
        f.write(html)
    return html_path
