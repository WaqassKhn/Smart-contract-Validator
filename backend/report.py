from __future__ import annotations

import json
from pathlib import Path

from backend.models import AnalysisReport


def build_summary(report: AnalysisReport) -> str:
    if not report.findings:
        return "No vulnerabilities were reported by the configured static analyzers."
    return (
        f"Detected {report.finding_count} potential issue(s) in {report.contract_name}. "
        "Each finding includes a plain-English explanation, exploit path, likely impact, and remediation guidance."
    )


def report_to_json(report: AnalysisReport) -> str:
    return json.dumps(report.model_dump(), indent=2)


def report_to_html(report: AnalysisReport) -> str:
    finding_cards = []
    for finding in report.findings:
        scenario = "".join(f"<li>{step}</li>" for step in finding.exploit_scenario)
        corrected = ""
        if finding.corrected_code:
            corrected = f"<pre>{finding.corrected_code}</pre>"
        finding_cards.append(
            f"""
            <section class=\"card\">
                <h2>{finding.vulnerability}</h2>
                <p><strong>Severity:</strong> {finding.severity}</p>
                <p><strong>Location:</strong> {finding.location}</p>
                <p><strong>Description:</strong> {finding.description}</p>
                <h3>Explanation</h3>
                <p>{finding.simple_explanation}</p>
                <h3>Exploit Scenario</h3>
                <ol>{scenario}</ol>
                <h3>Impact</h3>
                <p>{finding.impact}</p>
                <h3>Fix Recommendation</h3>
                <p>{finding.fix_recommendation}</p>
                {corrected}
            </section>
            """
        )

    if not finding_cards:
        finding_cards.append("<section class='card'><h2>No findings</h2><p>No issues were reported.</p></section>")

    return f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"utf-8\" />
        <title>Smart Contract Security Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 32px;
                color: #222;
                background: #f5f7fb;
            }}
            .card {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
            }}
            pre {{
                background: #0f172a;
                color: #e2e8f0;
                padding: 16px;
                border-radius: 8px;
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
        <h1>AI Smart Contract Risk Explainer</h1>
        <p>{report.summary}</p>
        {''.join(finding_cards)}
    </body>
    </html>
    """


def save_html_report(report: AnalysisReport, destination: str | Path) -> Path:
    output_path = Path(destination)
    output_path.write_text(report_to_html(report), encoding="utf-8")
    return output_path


def save_json_report(report: AnalysisReport, destination: str | Path) -> Path:
    output_path = Path(destination)
    output_path.write_text(report_to_json(report), encoding="utf-8")
    return output_path


def save_pdf_report(report: AnalysisReport, destination: str | Path) -> Path:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    output_path = Path(destination)
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph("AI Smart Contract Risk Explainer", styles["Title"]), Spacer(1, 12)]
    story.append(Paragraph(report.summary, styles["BodyText"]))
    story.append(Spacer(1, 12))

    for finding in report.findings:
        story.append(Paragraph(f"{finding.vulnerability} ({finding.severity})", styles["Heading2"]))
        story.append(Paragraph(f"Location: {finding.location}", styles["BodyText"]))
        story.append(Paragraph(finding.simple_explanation, styles["BodyText"]))
        story.append(Paragraph(f"Impact: {finding.impact}", styles["BodyText"]))
        story.append(Paragraph(f"Fix: {finding.fix_recommendation}", styles["BodyText"]))
        story.append(Spacer(1, 12))

    doc.build(story)
    return output_path
