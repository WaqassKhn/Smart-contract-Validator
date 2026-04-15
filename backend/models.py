from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AnalysisTarget(BaseModel):
    contract_name: str = Field(default="UploadedContract")
    source_code: str
    filename: str | None = None


class VulnerabilityFinding(BaseModel):
    vulnerability: str
    severity: str = "Medium"
    confidence: str = "Medium"
    location: str = "Unknown"
    function: str | None = None
    description: str
    detector: str
    code_snippet: str | None = None
    tool: str = "slither"
    raw: dict[str, Any] = Field(default_factory=dict)


class ExplainedFinding(VulnerabilityFinding):
    simple_explanation: str
    exploit_scenario: list[str]
    impact: str
    fix_recommendation: str
    corrected_code: str | None = None


class AnalysisReport(BaseModel):
    contract_name: str
    source: str
    finding_count: int
    findings: list[ExplainedFinding]
    summary: str
    tool_status: dict[str, str] = Field(default_factory=dict)
