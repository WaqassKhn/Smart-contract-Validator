from __future__ import annotations

from typing import Any

from backend.models import VulnerabilityFinding


SEVERITY_MAP = {
    "High": "High",
    "Medium": "Medium",
    "Low": "Low",
    "Informational": "Low",
    "Optimization": "Low",
}


KEYWORD_SEVERITY = {
    "reentrancy": "High",
    "arbitrary from": "High",
    "arbitrary send": "High",
    "suicidal": "High",
    "tx.origin": "High",
    "uninitialized storage": "High",
    "integer overflow": "High",
    "access control": "High",
    "shadowing": "Medium",
    "timestamp": "Medium",
    "unchecked": "Medium",
}


def _guess_severity(check: str, impact: str | None) -> str:
    if impact and impact in SEVERITY_MAP:
        return SEVERITY_MAP[impact]

    normalized = check.lower()
    for keyword, severity in KEYWORD_SEVERITY.items():
        if keyword in normalized:
            return severity
    return "Medium"


def _extract_location(element: dict[str, Any]) -> tuple[str, str | None, str | None]:
    source_mapping = element.get("source_mapping") or {}
    lines = source_mapping.get("lines") or []
    first_line = lines[0] if lines else "?"

    name = element.get("name")
    type_specific = element.get("type_specific_fields") or {}
    function = type_specific.get("parent", {}).get("name") or name
    file_name = source_mapping.get("filename_short") or source_mapping.get("filename_relative") or "contract.sol"

    location = f"{file_name}:{first_line}"
    if function:
        location = f"{location} ({function})"
    return location, function, name


def parse_slither_output(payload: dict[str, Any]) -> list[VulnerabilityFinding]:
    results = payload.get("results") or {}
    detectors = results.get("detectors") or []

    findings: list[VulnerabilityFinding] = []
    for detector in detectors:
        elements = detector.get("elements") or [{}]
        primary_element = elements[0] if elements else {}
        location, function, _ = _extract_location(primary_element)
        description = (detector.get("description") or detector.get("check") or "").strip()

        findings.append(
            VulnerabilityFinding(
                vulnerability=detector.get("check", "Unknown detector"),
                severity=_guess_severity(detector.get("check", ""), detector.get("impact")),
                confidence=detector.get("confidence", "Medium"),
                location=location,
                function=function,
                description=description,
                detector=detector.get("check", "unknown"),
                code_snippet=None,
                tool="slither",
                raw=detector,
            )
        )
    return findings


def parse_mythril_output(payload: dict[str, Any]) -> list[VulnerabilityFinding]:
    issues = payload.get("issues") or []
    findings: list[VulnerabilityFinding] = []

    for issue in issues:
        findings.append(
            VulnerabilityFinding(
                vulnerability=issue.get("title", "Unknown Mythril issue"),
                severity=issue.get("severity", "Medium"),
                confidence="Medium",
                location=f"{issue.get('filename', 'contract.sol')}:{issue.get('lineno', '?')}",
                function=issue.get("function"),
                description=issue.get("description", "").strip(),
                detector=issue.get("swc-id", "mythril"),
                code_snippet=issue.get("code"),
                tool="mythril",
                raw=issue,
            )
        )
    return findings
