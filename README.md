# Smart Contract Validator

Smart Contract Validator is an AI-assisted Solidity security analysis project. It scans smart contracts with static analysis tools, converts the raw findings into structured data, and explains those findings in plain English through a FastAPI backend and a Streamlit frontend.

This repository is designed for academic demos, project submissions, and beginner-friendly smart contract security walkthroughs.

The current prototype supports:

- Solidity source upload or pasted source input
- Slither as the primary analyzer
- Optional Mythril analysis
- Groq or OpenAI powered explanations with a rule-based fallback
- JSON, HTML, and PDF report generation
- Sample vulnerable and safer Solidity contracts for demonstration

## What this project does

- Accepts Solidity contracts through file upload or pasted code
- Runs `Slither` as the main static analyzer
- Optionally runs `Mythril` as a deeper secondary analyzer
- Normalizes analyzer output into structured vulnerability findings
- Explains findings in plain English with exploit scenario, impact, and fix guidance
- Generates JSON, HTML, and PDF-style reports
- Provides a Streamlit demo UI and a FastAPI backend
- Supports Groq as the preferred LLM provider and OpenAI as an optional fallback

## What this project can do

- Detect common smart contract risks reported by static tools
- Turn raw scanner output into a structured report format
- Explain technical vulnerabilities in simpler language
- Support class demos with sample vulnerable contracts
- Export reports for submission or presentation

## Project structure

```text
project/
├── backend/
│   ├── __init__.py
│   ├── ai_engine.py
│   ├── analyzer.py
│   ├── main.py
│   ├── models.py
│   ├── parser.py
│   └── report.py
├── frontend/
│   └── app.py
├── samples/
│   ├── access_control_vulnerable.sol
│   ├── integer_overflow_legacy.sol
│   ├── reentrancy_vulnerable.sol
│   ├── safe_vault.sol
│   └── sample_report.json
├── .gitignore
├── requirements.txt
└── README.md
```

## Architecture

```text
[Frontend UI / API Client]
            |
            v
       [Backend API]
            |
            v
 [Static Analyzer Layer]
            |
            v
          [Parser]
            |
            v
 [Groq / OpenAI / Rules]
            |
            v
   [JSON / HTML / PDF Report]
```

## Processing pipeline

1. User uploads a Solidity file or pastes source code.
2. Backend stores the contract in a temporary file.
3. Slither scans the contract and returns JSON output.
4. Parser converts the raw tool output into normalized findings.
5. AI layer generates explanation, exploit scenario, impact, and fix recommendation.
6. Report layer prepares JSON, HTML, and PDF exports.

## Step-by-step setup and run guide

These steps are written for Windows PowerShell because that is the environment used for this project. A short macOS / Linux note is included later.

### 1. Open the project folder

If using Git:

```powershell
git clone <your-repository-url>
Set-Location ETHBlockchain
```

If you already have the folder:

```powershell
Set-Location "I:\SeM_6\CS&BC\ETHBlockchain"
```

### 2. Check Python

Use Python `3.11` or newer.

```powershell
python --version
```

If this command fails, install Python first and reopen PowerShell.

### 3. Create the virtual environment

```powershell
python -m venv .venv
```

### 4. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, your prompt should show `(.venv)`.

### 5. Install the Python dependencies

```powershell
python -m pip install -r requirements.txt
python -m pip install slither-analyzer
```

Optional:

```powershell
python -m pip install mythril
```

### 6. Make sure the venv tools are on `PATH`

This project depends on command-line tools such as `slither` and `solc`. In this repository they are typically installed under `.venv\Scripts`, so add that folder to your current PowerShell session:

```powershell
$env:Path = "$PWD\.venv\Scripts;$env:Path"
```

Check that PowerShell can now find the tools:

```powershell
slither --version
solc --version
```

If `slither --version` works but `solc --version` fails, continue to the next step.

### 7. Install a Solidity compiler version for your contracts

Many sample and test contracts in this project use:

```solidity
pragma solidity ^0.8.20;
```

Install and select that compiler version:

```powershell
python -m pip install solc-select
solc-select install 0.8.20
solc-select use 0.8.20
solc --version
```

If you analyze contracts with a different pragma, install a matching compiler version instead.

### 8. Optional: configure the AI provider

The AI layer supports three modes:

- `groq`
- `openai`
- `rule-based`

If no provider is configured, the app falls back to rule-based explanations when needed.

Recommended Groq setup:

```powershell
$env:LLM_PROVIDER="groq"
$env:GROQ_API_KEY="your_groq_api_key_here"
$env:GROQ_MODEL="llama-3.3-70b-versatile"
```

Optional OpenAI setup:

```powershell
$env:LLM_PROVIDER="openai"
$env:OPENAI_API_KEY="your_openai_api_key_here"
$env:OPENAI_MODEL="gpt-4.1-mini"
```

### 9. Run the Streamlit UI

Start the app from the project root while the virtual environment is still active:

```powershell
streamlit run frontend\app.py
```

If `streamlit` is not found, use:

```powershell
python -m streamlit run frontend\app.py
```

### 10. Use the app

1. Open the local Streamlit URL shown in the terminal.
2. Enter a contract label if you want.
3. Upload a `.sol` file or paste Solidity code.
4. Click `Analyze Contract`.
5. Review the findings and download JSON, HTML, or PDF if needed.

For a quick test, upload:

- `samples\reentrancy_vulnerable.sol`
- `samples\safe_vault.sol`

## FastAPI backend run steps

If you want to run the API directly instead of the Streamlit UI:

```powershell
uvicorn backend.main:app --reload
```

Default local URL:

```text
http://127.0.0.1:8000
```

Available endpoints:

- `GET /health`
- `POST /analyze/text`
- `POST /analyze/file`

If `/analyze/file` support is missing, install:

```powershell
python -m pip install python-multipart
```

### Example API call

```bash
curl -X POST "http://127.0.0.1:8000/analyze/text" \
  -H "Content-Type: application/json" \
  -d "{\"contract_name\":\"Demo\",\"source_code\":\"pragma solidity ^0.8.20; contract Demo { }\"}"
```

## Sample contracts included

The `samples/` directory contains test contracts for the demo:

- `reentrancy_vulnerable.sol`
- `access_control_vulnerable.sol`
- `integer_overflow_legacy.sol`
- `safe_vault.sol`
- `sample_report.json`

These cover the main project cases: vulnerable contracts and a safer comparison contract.

## Example finding format

```json
{
  "vulnerability": "reentrancy-eth",
  "severity": "High",
  "location": "reentrancy_vulnerable.sol:12 (withdraw)",
  "description": "External call before state update",
  "simple_explanation": "This function can be entered again before internal state is updated.",
  "exploit_scenario": [
    "Attacker deposits funds.",
    "Attacker calls withdraw().",
    "The contract sends ETH before balance update.",
    "The attacker re-enters and drains funds."
  ],
  "impact": "Loss of contract funds.",
  "fix_recommendation": "Update state before external interaction and add a reentrancy guard."
}
```

## Troubleshooting

### `slither` is not recognized

Your virtual environment is either not activated or `.venv\Scripts` is not on `PATH`.

Run:

```powershell
.\.venv\Scripts\Activate.ps1
$env:Path = "$PWD\.venv\Scripts;$env:Path"
slither --version
```

### `solc` is not recognized

Install and select a compiler version:

```powershell
python -m pip install solc-select
solc-select install 0.8.20
solc-select use 0.8.20
solc --version
```

### Slither says it could not find the Solidity compiler

This usually means one of these:

- `solc` is not installed
- `solc` is installed but not on `PATH`
- the contract pragma does not match the installed compiler version

Checks:

```powershell
slither --version
solc --version
```

If your contract uses `pragma solidity ^0.8.20;`, make sure `0.8.20` is installed and selected.

### The app shows a compiler error after upload

Check the uploaded contract first:

- it should be valid Solidity source code
- it should compile with the selected `solc` version
- any imported files must also be available

### Streamlit says `No module named 'backend'`

Run Streamlit from the project root:

```powershell
streamlit run frontend\app.py
```

### `python-multipart` is missing

Install it if you want `/analyze/file` support:

```powershell
python -m pip install python-multipart
```

## Suggested demo flow

1. Activate `.venv`.
2. Add `.venv\Scripts` to `PATH`.
3. Confirm `slither --version` and `solc --version` both work.
4. Start the Streamlit app.
5. Upload `samples\reentrancy_vulnerable.sol`.
6. Show the detected issue and explanation.
7. Export the report as JSON or HTML.
8. Repeat with `samples\safe_vault.sol` to compare output.

## macOS / Linux note

If you are not on Windows, the flow is the same but activation changes:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install slither-analyzer solc-select
```

Run commands from the project root after activation.

## Important limitations

- Static analyzers do not prove exploitability.
- Real smart contract audits still need human review.
- Some contracts require a matching Solidity compiler version on the machine.
- AI-generated explanations improve readability, but they should still be verified.

## Future improvements

- Multi-file contract project support
- Stronger code snippet extraction around vulnerable lines
- Better report styling for PDF exports
- Report history and persistence
- Severity score aggregation across analyzers
