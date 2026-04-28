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

DETECTOR_METADATA = {
    "reentrancy-eth": {"title": "Reentrancy", "category": "State management"},
    "reentrancy-no-eth": {"title": "Reentrancy", "category": "State management"},
    "tx-origin": {"title": "tx.origin Authentication", "category": "Access control"},
    "arbitrary-send-eth": {"title": "Arbitrary ETH Transfer", "category": "Access control"},
    "controlled-delegatecall": {"title": "Controlled Delegatecall", "category": "External calls"},
    "delegatecall-loop": {"title": "Unsafe Delegatecall Pattern", "category": "External calls"},
    "suicidal": {"title": "Unprotected Selfdestruct", "category": "Access control"},
    "timestamp": {"title": "Timestamp Dependence", "category": "Entropy / time"},
    "unchecked-send": {"title": "Unchecked ETH Send", "category": "External calls"},
    "unchecked-transfer": {"title": "Unchecked Token Transfer", "category": "External calls"},
    "weak-prng": {"title": "Weak Randomness", "category": "Entropy / time"},
    "unprotected-upgrade": {"title": "Unprotected Upgradeability", "category": "Access control"},
}

NOISE_DETECTORS = {
    "solc-version",
    "low-level-calls",
}

KEYWORD_SEVERITY = {
    "reentrancy": "High",
    "delegatecall": "High",
    "tx.origin": "High",
    "arbitrary": "High",
    "selfdestruct": "High",
    "suicidal": "High",
    "timestamp": "Medium",
    "unchecked": "Medium",
}

SEVERITY_ORDER = {
    "High": 0,
    "Medium": 1,
    "Low": 2,
}


def _guess_severity(check: str, impact: str | None) -> str:
    if impact and impact in SEVERITY_MAP:
        return SEVERITY_MAP[impact]

    normalized = check.lower()
    for keyword, severity in KEYWORD_SEVERITY.items():
        if keyword in normalized:
            return severity
    return "Medium"


def _clean_description(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "No description was provided by the analyzer."
    summary = lines[0]
    if len(summary) > 220:
        return summary[:217].rstrip() + "..."
    return summary


def _extract_location(element: dict[str, Any]) -> tuple[str, str | None, int | None]:
    source_mapping = element.get("source_mapping") or {}
    lines = source_mapping.get("lines") or []
    first_line = lines[0] if lines else None

    name = element.get("name")
    type_specific = element.get("type_specific_fields") or {}
    function = type_specific.get("parent", {}).get("name") or name
    file_name = source_mapping.get("filename_short") or source_mapping.get("filename_relative") or "contract.sol"

    location = f"{file_name}:{first_line or '?'}"
    if function:
        location = f"{location} ({function})"
    return location, function, first_line


def _extract_code_snippet(source_code: str, line_number: int | None, span: int = 5) -> str | None:
    if not source_code or not line_number:
        return None

    lines = source_code.splitlines()
    start = max(0, line_number - 2)
    end = min(len(lines), start + span)
    snippet_lines = []
    for index in range(start, end):
        snippet_lines.append(f"{index + 1:>4}: {lines[index]}")
    return "\n".join(snippet_lines) if snippet_lines else None


def _normalize_title(check: str) -> tuple[str, str]:
    metadata = DETECTOR_METADATA.get(check, {})
    if metadata:
        return metadata["title"], metadata["category"]

    title = check.replace("-", " ").replace("_", " ").title()
    return title, "General"


def _is_noise(detector: dict[str, Any]) -> bool:
    check = detector.get("check", "")
    if check in NOISE_DETECTORS:
        return True
    return detector.get("impact") in {"Informational", "Optimization"}


def _deduplicate(findings: list[VulnerabilityFinding]) -> list[VulnerabilityFinding]:
    unique: dict[tuple[str, str], VulnerabilityFinding] = {}
    for finding in findings:
        key = (finding.detector, finding.location)
        if key not in unique:
            unique[key] = finding
    return sorted(
        unique.values(),
        key=lambda item: (SEVERITY_ORDER.get(item.severity, 9), item.line_number or 999999, item.vulnerability),
    )


def parse_slither_output(
    payload: dict[str, Any],
    source_code: str = "",
    filename: str | None = None,
) -> list[VulnerabilityFinding]:
    results = payload.get("results") or {}
    detectors = results.get("detectors") or []

    findings: list[VulnerabilityFinding] = []
    for detector in detectors:
        if _is_noise(detector):
            continue

        elements = detector.get("elements") or [{}]
        primary_element = elements[0] if elements else {}
        location, function, line_number = _extract_location(primary_element)
        description = _clean_description(detector.get("description") or detector.get("check") or "")
        title, category = _normalize_title(detector.get("check", "Unknown detector"))

        findings.append(
            VulnerabilityFinding(
                vulnerability=title,
                severity=_guess_severity(detector.get("check", ""), detector.get("impact")),
                confidence=detector.get("confidence", "Medium"),
                category=category,
                location=location,
                function=function,
                line_number=line_number,
                description=description,
                detector=detector.get("check", "unknown"),
                code_snippet=_extract_code_snippet(source_code, line_number),
                tool="slither",
                raw=detector,
            )
        )
    return _deduplicate(findings)


def parse_mythril_output(payload: dict[str, Any]) -> list[VulnerabilityFinding]:
    issues = payload.get("issues") or []
    findings: list[VulnerabilityFinding] = []

    for issue in issues:
        title = issue.get("title", "Unknown Mythril issue")
        findings.append(
            VulnerabilityFinding(
                vulnerability=title,
                severity=issue.get("severity", "Medium"),
                confidence="Medium",
                category="Mythril finding",
                location=f"{issue.get('filename', 'contract.sol')}:{issue.get('lineno', '?')}",
                function=issue.get("function"),
                line_number=issue.get("lineno"),
                description=_clean_description(issue.get("description", "")),
                detector=issue.get("swc-id", "mythril"),
                code_snippet=issue.get("code"),
                tool="mythril",
                raw=issue,
            )
        )
    return _deduplicate(findings)
