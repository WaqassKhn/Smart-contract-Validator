from __future__ import annotations

import json
import os

from backend.models import ExplainedFinding, VulnerabilityFinding


PROMPT_TEMPLATE = """You are a smart contract security auditor.

Given:
- Vulnerability type: {vulnerability}
- Severity: {severity}
- Location: {location}
- Description: {description}
- Code snippet:
{code_snippet}

Explain:
1. What the vulnerability is
2. How it can be exploited step by step
3. What damage it can cause
4. How to fix it with corrected Solidity code when possible

Return strict JSON with keys:
simple_explanation, exploit_scenario, impact, fix_recommendation, corrected_code

Keep it simple but technically accurate.
"""


RULE_BASED_EXPLANATIONS = {
    "reentrancy": {
        "simple_explanation": "This code can call an external address before it finishes updating its own state. An attacker can use that callback window to enter the function again and repeat the withdrawal logic.",
        "exploit_scenario": [
            "The attacker deposits or becomes eligible to withdraw funds.",
            "The vulnerable function sends ETH or invokes external code before reducing the attacker's balance.",
            "The attacker's fallback function calls the vulnerable function again before state is updated.",
            "The cycle repeats until contract funds are drained.",
        ],
        "impact": "High risk of complete or near-complete fund loss from the affected contract.",
        "fix_recommendation": "Use the Checks-Effects-Interactions pattern, update balances before external calls, and consider a reentrancy guard.",
        "corrected_code": "balances[msg.sender] -= amount;\npayable(msg.sender).transfer(amount);",
    },
    "access control": {
        "simple_explanation": "A sensitive function can be called by accounts that should not have permission. That makes admin-only actions reachable by attackers.",
        "exploit_scenario": [
            "An attacker identifies a privileged function without a proper ownership or role check.",
            "The attacker calls the function directly from an untrusted account.",
            "The contract performs the restricted action because no authorization stops it.",
            "Funds, ownership, or critical configuration can then be changed maliciously.",
        ],
        "impact": "Attackers may seize control of admin functionality, withdraw funds, or reconfigure the contract.",
        "fix_recommendation": "Protect sensitive functions with explicit authorization such as onlyOwner or role-based access checks.",
        "corrected_code": "modifier onlyOwner() {\n    require(msg.sender == owner, \"not owner\");\n    _;\n}",
    },
    "integer overflow": {
        "simple_explanation": "Arithmetic can exceed the allowed numeric range and wrap to an unexpected value, which can corrupt balances or bypass limits.",
        "exploit_scenario": [
            "The attacker triggers arithmetic near the maximum allowed integer value.",
            "The value wraps around instead of staying within the intended range.",
            "The contract accepts the corrupted value and continues execution.",
            "Balance checks, caps, or accounting logic can then be bypassed.",
        ],
        "impact": "Incorrect accounting can lead to unauthorized minting, broken limits, or fund manipulation.",
        "fix_recommendation": "Use Solidity 0.8+ checked arithmetic or explicit safe math patterns where older compiler versions are required.",
        "corrected_code": "totalSupply += amount; // Solidity 0.8+ reverts automatically on overflow",
    },
}


def _rule_based_response(finding: VulnerabilityFinding) -> ExplainedFinding:
    normalized = finding.vulnerability.lower()
    template = None
    for keyword, explanation in RULE_BASED_EXPLANATIONS.items():
        if keyword in normalized:
            template = explanation
            break

    if template is None:
        template = {
            "simple_explanation": "The static analyzer found a risky pattern that may expose the contract to unexpected behavior or abuse.",
            "exploit_scenario": [
                "An attacker identifies the reachable risky code path.",
                "The attacker triggers the function with crafted inputs or call ordering.",
                "The risky behavior causes the contract to violate intended security assumptions.",
            ],
            "impact": "The contract may lose funds, integrity, or admin control depending on how this code is used.",
            "fix_recommendation": "Review the flagged logic, add explicit validation and authorization, and align the implementation with secure Solidity patterns.",
            "corrected_code": None,
        }

    return ExplainedFinding(**finding.model_dump(), **template)


def _extract_json_payload(content: str) -> dict | None:
    text = content.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return None
        return None


def _build_prompt(finding: VulnerabilityFinding) -> str:
    return PROMPT_TEMPLATE.format(
        vulnerability=finding.vulnerability,
        severity=finding.severity,
        location=finding.location,
        description=finding.description,
        code_snippet=finding.code_snippet or "Snippet not available from analyzer output.",
    )


def _to_explained_finding(finding: VulnerabilityFinding, parsed: dict | None) -> ExplainedFinding:
    if not parsed:
        return _rule_based_response(finding)

    return ExplainedFinding(
        **finding.model_dump(),
        simple_explanation=parsed.get("simple_explanation", ""),
        exploit_scenario=parsed.get("exploit_scenario", []),
        impact=parsed.get("impact", ""),
        fix_recommendation=parsed.get("fix_recommendation", ""),
        corrected_code=parsed.get("corrected_code"),
    )


def _groq_response(finding: VulnerabilityFinding) -> ExplainedFinding:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _rule_based_response(finding)

    try:
        from groq import Groq
    except ImportError:
        return _rule_based_response(finding)

    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": "You are a smart contract security auditor. Return strict JSON only.",
            },
            {
                "role": "user",
                "content": _build_prompt(finding),
            },
        ],
    )
    content = completion.choices[0].message.content or ""
    return _to_explained_finding(finding, _extract_json_payload(content))


def _openai_response(finding: VulnerabilityFinding) -> ExplainedFinding:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _rule_based_response(finding)

    try:
        from openai import OpenAI
    except ImportError:
        return _rule_based_response(finding)

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        input=_build_prompt(finding),
    )
    content = response.output_text
    return _to_explained_finding(finding, _extract_json_payload(content))


def _provider_response(finding: VulnerabilityFinding) -> ExplainedFinding:
    provider = os.getenv("LLM_PROVIDER", "auto").lower()

    if provider == "groq":
        return _groq_response(finding)
    if provider == "openai":
        return _openai_response(finding)
    if provider == "rule-based":
        return _rule_based_response(finding)

    if os.getenv("GROQ_API_KEY"):
        return _groq_response(finding)
    if os.getenv("OPENAI_API_KEY"):
        return _openai_response(finding)
    return _rule_based_response(finding)


def explain_finding(finding: VulnerabilityFinding) -> ExplainedFinding:
    return _provider_response(finding)


def explain_findings(findings: list[VulnerabilityFinding]) -> list[ExplainedFinding]:
    return [explain_finding(finding) for finding in findings]
