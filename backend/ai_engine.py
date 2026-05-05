from __future__ import annotations

import json
import os

from backend.models import ExplainedFinding, VulnerabilityFinding


PROMPT_TEMPLATE = """You are a smart contract security auditor.

Given:
- Vulnerability type: {vulnerability}
- Severity: {severity}
- Category: {category}
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

Keep it concise, simple, and technically accurate.
"""


RULE_BASED_EXPLANATIONS = {
    "reentrancy": {
        "simple_explanation": "This function makes an external call before it finishes updating internal state. That lets an attacker call back into the contract before the first execution is complete.",
        "exploit_scenario": [
            "The attacker becomes eligible to withdraw funds.",
            "The vulnerable function sends ETH before reducing the attacker's balance.",
            "The attacker's fallback code re-enters the same function before state is updated.",
            "The repeated calls drain more funds than intended.",
        ],
        "impact": "Contract funds can be drained or accounting can become inconsistent.",
        "fix_recommendation": "Apply Checks-Effects-Interactions, update state before external calls, and consider a reentrancy guard.",
        "corrected_code": "balances[msg.sender] -= amount;\npayable(msg.sender).transfer(amount);",
    },
    "tx.origin": {
        "simple_explanation": "The contract is using tx.origin for authorization. That value can be influenced through intermediate contracts, so it is not safe for access control.",
        "exploit_scenario": [
            "The victim interacts with an attacker-controlled contract.",
            "That malicious contract forwards a call into the vulnerable contract.",
            "The vulnerable contract checks tx.origin instead of msg.sender.",
            "The attacker gains access because tx.origin still points to the victim account.",
        ],
        "impact": "Privileged functions may be executed by an attacker through phishing or proxy calls.",
        "fix_recommendation": "Use msg.sender for authorization and protect sensitive functions with explicit ownership or role checks.",
        "corrected_code": "require(msg.sender == owner, \"not owner\");",
    },
    "access control": {
        "simple_explanation": "A sensitive function can be reached without proper authorization checks. That makes admin-only behavior available to untrusted callers.",
        "exploit_scenario": [
            "The attacker identifies a function that changes ownership, sends funds, or destroys the contract.",
            "The function has no effective caller restriction.",
            "The attacker calls it directly from an untrusted account.",
            "Privileged state changes or fund transfers happen immediately.",
        ],
        "impact": "Attackers may take ownership, withdraw funds, or disable the contract.",
        "fix_recommendation": "Restrict sensitive functions with onlyOwner or role-based access control and validate privileged parameters.",
        "corrected_code": "modifier onlyOwner() {\n    require(msg.sender == owner, \"not owner\");\n    _;\n}",
    },
    "timestamp": {
        "simple_explanation": "The contract relies on block timestamps for critical logic such as randomness or reward conditions. Miners and validators can influence timestamps slightly.",
        "exploit_scenario": [
            "An attacker targets a function whose outcome depends on block.timestamp.",
            "The transaction is timed so the timestamp-based branch becomes favorable.",
            "The contract makes a security-sensitive decision using that timestamp value.",
            "The attacker gains an unfair payout or bypasses intended controls.",
        ],
        "impact": "Time-sensitive outcomes, lotteries, or unlock conditions can be manipulated within a limited window.",
        "fix_recommendation": "Do not use block.timestamp for randomness or high-trust decisions. Use verifiable randomness or stronger validation logic.",
        "corrected_code": None,
    },
    "delegatecall": {
        "simple_explanation": "The contract exposes delegatecall behavior in a way that may let untrusted code run inside the contract's storage context.",
        "exploit_scenario": [
            "An attacker controls the target address or calldata passed into delegatecall.",
            "The contract executes foreign code using its own storage and permissions.",
            "That code overwrites critical state such as owner or balances.",
            "The attacker gains control or steals assets.",
        ],
        "impact": "Delegatecall misuse can lead to full contract takeover.",
        "fix_recommendation": "Avoid delegatecall to untrusted addresses. Lock implementation addresses and strictly validate upgrade paths.",
        "corrected_code": None,
    },
    "selfdestruct": {
        "simple_explanation": "The contract exposes selfdestruct-like behavior without strong protections. An attacker may be able to destroy the contract or redirect remaining funds.",
        "exploit_scenario": [
            "The attacker calls the destructive function directly.",
            "The contract does not enforce a strong ownership or governance check.",
            "The contract is destroyed or its balance is redirected.",
            "Users lose access to the deployed application and its assets.",
        ],
        "impact": "The contract can be permanently disabled and any remaining funds can be lost or stolen.",
        "fix_recommendation": "Avoid destructive functionality unless absolutely necessary and protect it with strict access control.",
        "corrected_code": None,
    },
    "unchecked": {
        "simple_explanation": "The contract performs an external interaction without checking the result carefully. Failed calls may go unnoticed and leave the system in an unsafe state.",
        "exploit_scenario": [
            "The attacker causes an external call to fail or behave unexpectedly.",
            "The contract ignores the result and continues execution.",
            "Internal accounting assumes the interaction succeeded.",
            "Users or the protocol are left with inconsistent state.",
        ],
        "impact": "Funds can become stuck, accounting can drift, or recovery logic can be bypassed.",
        "fix_recommendation": "Check return values from low-level calls and revert when external interactions fail.",
        "corrected_code": "require(success, \"external call failed\");",
    },
}


def _rule_based_response(finding: VulnerabilityFinding) -> ExplainedFinding:
    normalized = f"{finding.vulnerability} {finding.detector}".lower()
    template = None
    for keyword, explanation in RULE_BASED_EXPLANATIONS.items():
        if keyword in normalized:
            template = explanation
            break

    if template is None:
        template = {
            "simple_explanation": "The analyzer found a risky contract pattern that may break security assumptions or expose sensitive behavior.",
            "exploit_scenario": [
                "An attacker identifies the vulnerable code path.",
                "The attacker triggers the function with crafted inputs or call ordering.",
                "The contract executes behavior that violates its intended trust model.",
            ],
            "impact": "The contract may lose funds, integrity, availability, or administrative control depending on how the pattern is reachable.",
            "fix_recommendation": "Review the flagged logic, reduce trust in external inputs, and protect sensitive flows with established Solidity security patterns.",
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
        category=finding.category,
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


def _gemini_response(finding: VulnerabilityFinding) -> ExplainedFinding:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _rule_based_response(finding)

    try:
        from google import genai
    except ImportError:
        return _rule_based_response(finding)

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=(
            "You are a smart contract security auditor. "
            "Return strict JSON only.\n\n"
            + _build_prompt(finding)
        ),
    )
    content = getattr(response, "text", "") or ""
    return _to_explained_finding(finding, _extract_json_payload(content))


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


def _provider_response(finding: VulnerabilityFinding) -> ExplainedFinding:
    provider = os.getenv("LLM_PROVIDER", "auto").lower()

    if provider == "gemini":
        return _gemini_response(finding)
    if provider == "groq":
        return _groq_response(finding)
    if provider == "rule-based":
        return _rule_based_response(finding)

    if os.getenv("GEMINI_API_KEY"):
        return _gemini_response(finding)
    if os.getenv("GROQ_API_KEY"):
        return _groq_response(finding)
    return _rule_based_response(finding)


def explain_finding(finding: VulnerabilityFinding) -> ExplainedFinding:
    return _provider_response(finding)


def explain_findings(findings: list[VulnerabilityFinding]) -> list[ExplainedFinding]:
    return [explain_finding(finding) for finding in findings]
