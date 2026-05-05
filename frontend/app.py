from __future__ import annotations

import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from backend.main import analyze_contract
from backend.models import AnalysisTarget
from backend.report import report_to_html, report_to_json, save_pdf_report


SEVERITY_COLORS = {
    "High": "#8b1e1e",
    "Medium": "#9a5a00",
    "Low": "#1e4fa1",
}

SAMPLE_OPTIONS = {
    "Reentrancy Demo": "samples/reentrancy_vulnerable.sol",
    "Access Control Demo": "samples/access_control_vulnerable.sol",
    "tx.origin Demo": "samples/tx_origin_vulnerable.sol",
    "Timestamp Dependence Demo": "samples/timestamp_lottery_vulnerable.sol",
    "Selfdestruct Demo": "samples/selfdestruct_vulnerable.sol",
    "Safe Vault Demo": "samples/safe_vault.sol",
    "Safe Access Vault Demo": "samples/safe_access_vault.sol",
    "Safe Time Lock Demo": "samples/safe_time_lock.sol",
}

if "source_code_input" not in st.session_state:
    st.session_state.source_code_input = ""
if "selected_contract_name" not in st.session_state:
    st.session_state.selected_contract_name = "PastedContract"


st.set_page_config(page_title="AI Smart Contract Risk Explainer", layout="wide")

st.markdown(
    """
    <style>
        .hero {
            padding: 24px 28px;
            border-radius: 22px;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 45%, #164e63 100%);
            color: #f8fafc;
            margin-bottom: 20px;
        }
        .hero p {
            color: #cbd5e1;
            margin-bottom: 0;
        }
        .finding-card {
            background: #ffffff;
            border-radius: 18px;
            padding: 18px 20px;
            margin-bottom: 16px;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
            border-left: 8px solid #cbd5e1;
        }
        .finding-meta {
            color: #475569;
            font-size: 0.95rem;
            margin-bottom: 10px;
        }
        .pill-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin: 8px 0 18px 0;
        }
        .pill {
            background: #eef2ff;
            color: #1e293b;
            border-radius: 999px;
            padding: 6px 12px;
            font-size: 0.85rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <h1>AI Smart Contract Risk Explainer</h1>
        <p>Upload or paste a Solidity contract, run static analysis, and get a readable security report with severity, exploit path, impact, and remediation powered by Gemini or Groq.</p>
    </section>
    """,
    unsafe_allow_html=True,
)


def render_finding_card(finding) -> None:
    severity_color = SEVERITY_COLORS.get(finding.severity, "#64748b")
    st.markdown(
        f"""
        <div class="finding-card" style="border-left-color:{severity_color};">
            <div class="pill-row">
                <span class="pill">{finding.severity} severity</span>
                <span class="pill">{finding.category}</span>
                <span class="pill">{finding.confidence} confidence</span>
            </div>
            <h3 style="color:{severity_color};margin-bottom:6px;">{finding.vulnerability}</h3>
            <div class="finding-meta"><strong>Location:</strong> {finding.location}</div>
            <p>{finding.description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    explainer_tab, impact_tab, fix_tab = st.tabs(["Explanation", "Impact", "Fix"])
    with explainer_tab:
        st.write(finding.simple_explanation)
        if finding.exploit_scenario:
            st.markdown("**Exploit Scenario**")
            for step_number, step in enumerate(finding.exploit_scenario, start=1):
                st.write(f"{step_number}. {step}")
    with impact_tab:
        st.write(finding.impact)
    with fix_tab:
        st.write(finding.fix_recommendation)
        if finding.corrected_code:
            st.code(finding.corrected_code, language="solidity")

    if finding.code_snippet:
        with st.expander("Relevant code snippet"):
            st.code(finding.code_snippet, language="solidity")


def render_summary(report) -> None:
    high = report.severity_breakdown.get("High", 0)
    medium = report.severity_breakdown.get("Medium", 0)
    low = report.severity_breakdown.get("Low", 0)
    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Findings", report.finding_count)
    metric_2.metric("High", high)
    metric_3.metric("Medium", medium)
    metric_4.metric("Low", low)
    st.info(report.summary)


def load_sample_into_editor(sample_label: str) -> None:
    sample_path = PROJECT_ROOT / SAMPLE_OPTIONS[sample_label]
    st.session_state.source_code_input = sample_path.read_text(encoding="utf-8")
    st.session_state.selected_contract_name = Path(sample_path).stem


with st.sidebar:
    st.header("Run Options")
    llm_provider = st.selectbox("Preferred LLM", ["gemini", "groq"], index=0)
    use_mythril = st.checkbox(
        "Use Mythril fallback",
        value=False,
        help="Runs Mythril after Slither as an extra scan pass. This can catch some issues through a different analysis approach, but it may take longer and can produce additional noise.",
    )
    st.caption("High-signal Slither findings are prioritized. Informational-only detector noise is filtered from the main report.")
    st.markdown(
        """
        **LLM Providers**

        - Select Gemini or Groq here
        - Provide the matching API key in your environment
        - Gemini uses `GEMINI_API_KEY`
        - Groq uses `GROQ_API_KEY`
        """
    )
    selected_sample = st.selectbox("Load sample into editor", list(SAMPLE_OPTIONS))
    st.button(
        "Load Sample",
        use_container_width=True,
        on_click=load_sample_into_editor,
        args=(selected_sample,),
    )
    st.caption("Built-in demo contracts are available from the selector above.")

uploaded_file = st.file_uploader("Upload Solidity file", type=["sol"])
source_code = st.text_area(
    "Or paste Solidity code",
    height=320,
    key="source_code_input",
    placeholder="pragma solidity ^0.8.20;\n\ncontract Demo {\n    uint256 public value;\n}\n",
)

analyze_clicked = st.button("Analyze Contract", type="primary")

if analyze_clicked:
    import os

    file_contents = None
    filename = None
    if uploaded_file is not None:
        file_contents = uploaded_file.getvalue().decode("utf-8")
        filename = uploaded_file.name
        st.session_state.selected_contract_name = Path(filename).stem

    contract_source = file_contents or source_code
    if not contract_source.strip():
        st.error("Provide either a Solidity file or pasted Solidity source code.")
    else:
        try:
            with st.spinner("Running analysis and preparing the report..."):
                os.environ["LLM_PROVIDER"] = llm_provider
                contract_name = st.session_state.selected_contract_name or "PastedContract"
                report = analyze_contract(
                    AnalysisTarget(
                        contract_name=contract_name,
                        source_code=contract_source,
                        filename=filename,
                    ),
                    use_mythril=use_mythril,
                )
        except Exception as exc:
            st.error(str(exc))
            st.caption("This tool expects Solidity contract code or a .sol file upload.")
        else:
            render_summary(report)

            if not report.findings:
                st.success("No high-signal findings were reported for this contract.")
            else:
                for finding in report.findings:
                    render_finding_card(finding)

            json_payload = report_to_json(report)
            html_payload = report_to_html(report)

            export_1, export_2, export_3 = st.columns(3)
            with export_1:
                st.download_button(
                    "Download JSON",
                    data=json_payload,
                    file_name=f"{contract_name.lower().replace(' ', '_')}_report.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with export_2:
                st.download_button(
                    "Download HTML",
                    data=html_payload,
                    file_name=f"{contract_name.lower().replace(' ', '_')}_report.html",
                    mime="text/html",
                    use_container_width=True,
                )
            with export_3:
                try:
                    pdf_path = Path(tempfile.gettempdir()) / f"{contract_name.lower().replace(' ', '_')}_report.pdf"
                    save_pdf_report(report, pdf_path)
                except Exception:
                    st.button("PDF unavailable", disabled=True, use_container_width=True)
                else:
                    st.download_button(
                        "Download PDF",
                        data=pdf_path.read_bytes(),
                        file_name=pdf_path.name,
                        mime="application/pdf",
                        use_container_width=True,
                    )

            with st.expander("Analyzer details"):
                st.json(report.tool_status)
