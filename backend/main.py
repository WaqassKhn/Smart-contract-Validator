from __future__ import annotations

import importlib.util
import json

from fastapi import FastAPI, HTTPException

from backend.ai_engine import explain_findings
from backend.analyzer import AnalyzerError, run_mythril, run_slither
from backend.models import AnalysisReport, AnalysisTarget
from backend.parser import parse_mythril_output, parse_slither_output
from backend.report import build_severity_breakdown, build_summary


app = FastAPI(title="AI Smart Contract Risk Explainer")
MULTIPART_INSTALLED = importlib.util.find_spec("multipart") is not None


def _validate_source_code(source_code: str) -> None:
    stripped = source_code.strip()
    if not stripped:
        raise AnalyzerError("Provide Solidity source code or upload a .sol file.")

    lowered = stripped.lower()
    if "pragma solidity" in lowered or "contract " in lowered or "interface " in lowered or "library " in lowered:
        return

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        parsed = None

    if isinstance(parsed, dict):
        raise AnalyzerError(
            "The pasted input looks like JSON report data, not Solidity source code. Paste a smart contract or upload a .sol file."
        )

    raise AnalyzerError(
        "Input does not look like Solidity source code. Paste a contract containing `pragma solidity` or upload a .sol file."
    )


def analyze_contract(target: AnalysisTarget, use_mythril: bool = False) -> AnalysisReport:
    _validate_source_code(target.source_code)

    slither_payload, tool_status = run_slither(target)
    findings = parse_slither_output(slither_payload, target.source_code, target.filename)

    if use_mythril:
        mythril_payload, mythril_status = run_mythril(target)
        tool_status.update(mythril_status)
        if mythril_payload:
            findings.extend(parse_mythril_output(mythril_payload))

    explained = explain_findings(findings)
    severity_breakdown = build_severity_breakdown(explained)
    report = AnalysisReport(
        contract_name=target.contract_name,
        source=target.source_code,
        finding_count=len(explained),
        findings=explained,
        summary="",
        severity_breakdown=severity_breakdown,
        tool_status=tool_status,
    )
    report.summary = build_summary(report)
    return report


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "multipart_installed": str(MULTIPART_INSTALLED).lower(),
    }


@app.post("/analyze/text", response_model=AnalysisReport)
def analyze_text(payload: AnalysisTarget, use_mythril: bool = False) -> AnalysisReport:
    try:
        return analyze_contract(payload, use_mythril=use_mythril)
    except AnalyzerError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if MULTIPART_INSTALLED:
    from fastapi import File, Form, UploadFile

    @app.post("/analyze/file", response_model=AnalysisReport)
    async def analyze_file(
        file: UploadFile = File(...),
        contract_name: str = Form("UploadedContract"),
        use_mythril: bool = Form(False),
    ) -> AnalysisReport:
        source_code = (await file.read()).decode("utf-8")
        payload = AnalysisTarget(
            contract_name=contract_name,
            source_code=source_code,
            filename=file.filename,
        )
        try:
            return analyze_contract(payload, use_mythril=use_mythril)
        except AnalyzerError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
