from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from backend.models import AnalysisTarget


class AnalyzerError(RuntimeError):
    """Raised when a static analyzer cannot be executed successfully."""


def _write_temp_contract(target: AnalysisTarget) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="contract-analysis-"))
    filename = target.filename or f"{target.contract_name}.sol"
    contract_path = temp_dir / filename
    contract_path.write_text(target.source_code, encoding="utf-8")
    return contract_path


def _run_command(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        check=False,
        capture_output=True,
        text=True,
    )


def _try_parse_json_output(output: str) -> dict | None:
    text = (output or "").strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _is_usable_slither_payload(payload: dict | None) -> bool:
    if not payload:
        return False
    return isinstance(payload.get("results"), dict)


def _format_command_failure(tool_name: str, result: subprocess.CompletedProcess[str]) -> str:
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    combined = "\n".join(part for part in [stderr, stdout] if part).strip()

    if not combined:
        return f"{tool_name} failed without any stdout/stderr output."

    lowered = combined.lower()
    compiler_missing_markers = [
        "solc is not installed",
        "solc not found",
        "solc was not found",
        "unable to find solc",
        "could not find solc",
        "compiler not found",
    ]
    if any(marker in lowered for marker in compiler_missing_markers):
        return (
            f"{tool_name} could not find the Solidity compiler. Install `solc` or use a supported compiler setup, then try again.\n\n"
            f"Details:\n{combined}"
        )
    if "pragma" in lowered and ("version mismatch" in lowered or "requires different compiler" in lowered):
        return (
            f"{tool_name} hit a Solidity compiler version mismatch. The contract pragma does not match an available compiler version.\n\n"
            f"Details:\n{combined}"
        )

    return f"{tool_name} failed.\n\nDetails:\n{combined}"


def run_slither(target: AnalysisTarget) -> tuple[dict, dict[str, str]]:
    if not shutil.which("slither"):
        raise AnalyzerError(
            "Slither is not installed or not available on PATH. Install Slither before running analysis."
        )

    contract_path = _write_temp_contract(target)
    command = ["slither", str(contract_path), "--json", "-"]
    result = _run_command(command, cwd=contract_path.parent)
    payload = _try_parse_json_output(result.stdout)

    if result.returncode != 0 and not _is_usable_slither_payload(payload):
        raise AnalyzerError(_format_command_failure("Slither", result))

    if not _is_usable_slither_payload(payload):
        raise AnalyzerError(
            "Slither did not return usable JSON results. This usually means the contract did not compile cleanly or Slither emitted a non-JSON error."
        )

    status = {
        "slither": "ok" if result.returncode == 0 else f"ok_with_exit_code_{result.returncode}",
        "slither_command": " ".join(command),
    }
    return payload, status


def run_mythril(target: AnalysisTarget) -> tuple[dict | None, dict[str, str]]:
    if not shutil.which("myth"):
        return None, {"mythril": "not_installed"}

    contract_path = _write_temp_contract(target)
    command = ["myth", "analyze", str(contract_path), "-o", "json"]
    result = _run_command(command, cwd=contract_path.parent)

    if result.returncode != 0:
        return None, {"mythril": _format_command_failure("Mythril", result)}

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None, {"mythril": "Mythril failed: invalid JSON output"}

    return payload, {"mythril": "ok", "mythril_command": " ".join(command)}
