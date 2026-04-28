from __future__ import annotations

import html
import json
from pathlib import Path

from backend.models import AnalysisReport, ExplainedFinding


def build_severity_breakdown(findings: list[ExplainedFinding]) -> dict[str, int]:
    breakdown = {"High": 0, "Medium": 0, "Low": 0}
    for finding in findings:
        breakdown[finding.severity] = breakdown.get(finding.severity, 0) + 1
    return breakdown


def build_summary(report: AnalysisReport) -> str:
    if not report.findings:
        return "No high-signal vulnerabilities were reported by the configured analyzers for this contract."

    high = report.severity_breakdown.get("High", 0)
    medium = report.severity_breakdown.get("Medium", 0)
    low = report.severity_breakdown.get("Low", 0)
    return (
        f"Detected {report.finding_count} high-signal issue(s) in {report.contract_name}: "
        f"{high} high, {medium} medium, and {low} low severity."
    )


def report_to_json(report: AnalysisReport) -> str:
    return json.dumps(report.model_dump(), indent=2)


def _finding_card(finding: ExplainedFinding) -> str:
    scenario = "".join(f"<li>{html.escape(step)}</li>" for step in finding.exploit_scenario)
    snippet = ""
    if finding.code_snippet:
        snippet = f"<h3>Relevant Code</h3><pre>{html.escape(finding.code_snippet)}</pre>"
    corrected = ""
    if finding.corrected_code:
        corrected = f"<h3>Suggested Fix Snippet</h3><pre>{html.escape(finding.corrected_code)}</pre>"

    return f"""
    <section class="card severity-{finding.severity.lower()}">
        <div class="eyebrow">{html.escape(finding.category)} | {html.escape(finding.severity)} severity</div>
        <h2>{html.escape(finding.vulnerability)}</h2>
        <p class="meta"><strong>Location:</strong> {html.escape(finding.location)} | <strong>Confidence:</strong> {html.escape(finding.confidence)}</p>
        <p>{html.escape(finding.description)}</p>
        <h3>Explanation</h3>
        <p>{html.escape(finding.simple_explanation)}</p>
        <h3>Exploit Scenario</h3>
        <ol>{scenario}</ol>
        <h3>Impact</h3>
        <p>{html.escape(finding.impact)}</p>
        <h3>Fix Recommendation</h3>
        <p>{html.escape(finding.fix_recommendation)}</p>
        {snippet}
        {corrected}
    </section>
    """


def report_to_html(report: AnalysisReport) -> str:
    finding_cards = [_finding_card(finding) for finding in report.findings]

    if not finding_cards:
        finding_cards.append(
            "<section class='card severity-safe'><h2>No high-signal findings</h2><p>The configured analyzers did not report issues that passed the report filters.</p></section>"
        )

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>Smart Contract Security Report</title>
        <style>
            :root {{
                --bg: #f3f4f6;
                --ink: #111827;
                --muted: #4b5563;
                --card: #ffffff;
                --line: #d1d5db;
                --high: #991b1b;
                --medium: #b45309;
                --low: #1d4ed8;
                --safe: #166534;
            }}
            body {{
                font-family: "Segoe UI", Arial, sans-serif;
                margin: 32px;
                color: var(--ink);
                background: linear-gradient(180deg, #f8fafc 0%, var(--bg) 100%);
            }}
            .summary {{
                background: #0f172a;
                color: #f8fafc;
                border-radius: 18px;
                padding: 24px;
                margin-bottom: 24px;
            }}
            .metrics {{
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                margin-top: 14px;
            }}
            .metric {{
                background: rgba(255, 255, 255, 0.08);
                border-radius: 999px;
                padding: 8px 14px;
                font-size: 14px;
            }}
            .card {{
                background: var(--card);
                border-radius: 16px;
                padding: 22px;
                margin-bottom: 18px;
                box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
                border-left: 8px solid var(--line);
            }}
            .severity-high {{ border-left-color: var(--high); }}
            .severity-medium {{ border-left-color: var(--medium); }}
            .severity-low {{ border-left-color: var(--low); }}
            .severity-safe {{ border-left-color: var(--safe); }}
            .eyebrow {{
                color: var(--muted);
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }}
            .meta {{
                color: var(--muted);
            }}
            pre {{
                background: #111827;
                color: #e5e7eb;
                padding: 16px;
                border-radius: 10px;
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>
        <section class="summary">
            <h1>AI Smart Contract Risk Explainer</h1>
            <p>{html.escape(report.summary)}</p>
            <div class="metrics">
                <div class="metric">Total findings: {report.finding_count}</div>
                <div class="metric">High: {report.severity_breakdown.get("High", 0)}</div>
                <div class="metric">Medium: {report.severity_breakdown.get("Medium", 0)}</div>
                <div class="metric">Low: {report.severity_breakdown.get("Low", 0)}</div>
            </div>
        </section>
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
    from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer

    output_path = Path(destination)
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph("AI Smart Contract Risk Explainer", styles["Title"]), Spacer(1, 12)]
    story.append(Paragraph(report.summary, styles["BodyText"]))
    story.append(Spacer(1, 12))

    for finding in report.findings:
        story.append(Paragraph(f"{finding.vulnerability} ({finding.severity})", styles["Heading2"]))
        story.append(Paragraph(f"Category: {finding.category}", styles["BodyText"]))
        story.append(Paragraph(f"Location: {finding.location}", styles["BodyText"]))
        story.append(Paragraph(f"Confidence: {finding.confidence}", styles["BodyText"]))
        story.append(Paragraph(finding.simple_explanation, styles["BodyText"]))
        story.append(Paragraph(f"Impact: {finding.impact}", styles["BodyText"]))
        story.append(Paragraph(f"Fix: {finding.fix_recommendation}", styles["BodyText"]))
        if finding.code_snippet:
            story.append(Spacer(1, 6))
            story.append(Preformatted(finding.code_snippet, styles["Code"]))
        story.append(Spacer(1, 12))

    doc.build(story)
    return output_path
