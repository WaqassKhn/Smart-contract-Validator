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


st.set_page_config(page_title="AI Smart Contract Risk Explainer", layout="wide")

st.title("AI Smart Contract Risk Explainer")
st.caption("Upload or paste Solidity code, run Slither, and get an AI-assisted plain-English security report.")


def render_finding_card(finding) -> None:
    severity_color = {"High": "#b91c1c", "Medium": "#b45309", "Low": "#1d4ed8"}.get(finding.severity, "#475569")
    st.markdown(
        f"""
        <div style="border:1px solid #e2e8f0;border-radius:14px;padding:18px;margin-bottom:16px;background:#ffffff;">
            <h3 style="margin-bottom:8px;color:{severity_color};">{finding.vulnerability}</h3>
            <p><strong>Severity:</strong> {finding.severity}</p>
            <p><strong>Location:</strong> {finding.location}</p>
            <p><strong>Description:</strong> {finding.description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.subheader("Explanation")
    st.write(finding.simple_explanation)
    st.subheader("Exploit Scenario")
    for step in finding.exploit_scenario:
        st.write(f"- {step}")
    st.subheader("Impact")
    st.write(finding.impact)
    st.subheader("Fix Recommendation")
    st.write(finding.fix_recommendation)
    if finding.corrected_code:
        st.code(finding.corrected_code, language="solidity")


with st.sidebar:
    st.header("Options")
    contract_name = st.text_input("Contract label", value="UploadedContract")
    use_mythril = st.checkbox("Run Mythril fallback", value=False)
    st.markdown(
        """
        **Requirements**

        - `slither` available on PATH
        - Optional `myth` for deeper analysis
        - Preferred `GROQ_API_KEY` for live LLM explanations
        - Optional `OPENAI_API_KEY` fallback support
        - Optional `LLM_PROVIDER=groq|openai|rule-based`
        """
    )

uploaded_file = st.file_uploader("Upload Solidity file", type=["sol"])
source_code = st.text_area(
    "Or paste Solidity code",
    height=300,
    placeholder="Paste Solidity source here, for example:\n\npragma solidity ^0.8.20;\n\ncontract Demo {\n    uint256 public value;\n}",
)

if st.button("Analyze Contract", type="primary"):
    file_contents = None
    filename = None
    if uploaded_file is not None:
        file_contents = uploaded_file.getvalue().decode("utf-8")
        filename = uploaded_file.name

    contract_source = file_contents or source_code
    if not contract_source.strip():
        st.error("Provide either a Solidity file or pasted Solidity source code.")
    else:
        try:
            with st.spinner("Running static analysis and generating explanations..."):
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
            st.info("Tip: this tool expects Solidity contract code, not JSON report data.")
        else:
            st.success(report.summary)
            st.json(report.tool_status)

            if not report.findings:
                st.info("No findings were reported by the configured tools.")
            else:
                for finding in report.findings:
                    render_finding_card(finding)

            json_payload = report_to_json(report)
            html_payload = report_to_html(report)

            st.download_button(
                "Download JSON Report",
                data=json_payload,
                file_name=f"{contract_name.lower().replace(' ', '_')}_report.json",
                mime="application/json",
            )
            st.download_button(
                "Download HTML Report",
                data=html_payload,
                file_name=f"{contract_name.lower().replace(' ', '_')}_report.html",
                mime="text/html",
            )

            try:
                pdf_path = Path(tempfile.gettempdir()) / f"{contract_name.lower().replace(' ', '_')}_report.pdf"
                save_pdf_report(report, pdf_path)
            except Exception:
                pass
            else:
                st.download_button(
                    "Download PDF Report",
                    data=pdf_path.read_bytes(),
                    file_name=pdf_path.name,
                    mime="application/pdf",
                )
