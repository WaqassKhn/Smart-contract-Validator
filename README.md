# AI Smart Contract Risk Explainer

AI Smart Contract Risk Explainer is a Python-based smart contract security project. It takes Solidity source code, runs static analysis with Slither, optionally runs Mythril, normalizes the findings, and generates plain-English explanations with impact and remediation guidance.

The project is built for a blockchain and cyber security demo. Its value is not only detection, but also turning analyzer output into a readable report that is easier to understand and present.

## What the project does

- Accepts Solidity contracts from file upload or pasted source
- Runs Slither as the primary analyzer
- Optionally runs Mythril as a fallback analyzer
- Filters low-signal analyzer noise from the main report
- Normalizes findings into readable categories and severities
- Extracts relevant code snippets around flagged lines
- Explains findings using Gemini or Groq, with a built-in fallback when no API provider is configured
- Generates JSON, HTML, and PDF reports
- Provides a Streamlit UI and a FastAPI backend

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
│   ├── safe_access_vault.sol
│   ├── safe_time_lock.sol
│   ├── safe_vault.sol
│   ├── selfdestruct_vulnerable.sol
│   ├── timestamp_lottery_vulnerable.sol
│   ├── tx_origin_vulnerable.sol
│   └── sample_report.json
├── .gitignore
├── requirements.txt
└── README.md
```

## Architecture

```text
[Streamlit UI / API Client]
            |
            v
       [FastAPI Backend]
            |
            v
 [Slither / Mythril Layer]
            |
            v
          [Parser]
            |
            v
 [Gemini / Groq]
            |
            v
   [JSON / HTML / PDF Report]
```

## Processing pipeline

1. User uploads a `.sol` file or pastes Solidity source.
2. Backend validates the input and writes it to a temporary file.
3. Slither scans the contract and returns raw JSON findings.
4. Parser removes low-value informational noise and normalizes the rest.
5. AI layer explains each issue with exploit scenario, impact, and fix guidance.
6. Report layer produces clean output for UI and downloads.

## Setup on a fresh system

### 1. Get the project

```bash
git clone <your-repository-url>
cd ETHBlockchain
```

### 2. Install Python

Use Python `3.11` or newer.

```bash
python --version
```

### 3. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Install Slither

```bash
pip install slither-analyzer
slither --version
```

### 6. Optional: install Mythril

```bash
pip install mythril
myth version
```

### 7. Configure Gemini or Groq

Supported modes:

- `gemini`
- `groq`

If `LLM_PROVIDER` is not set, the code uses:

1. Gemini if `GEMINI_API_KEY` exists
2. Groq if `GROQ_API_KEY` exists
3. Rule-based explanations otherwise

Install Gemini SDK:

```bash
pip install google-genai
```

Gemini setup in Windows PowerShell:

```powershell
$env:LLM_PROVIDER="gemini"
$env:GEMINI_API_KEY="your_gemini_api_key_here"
$env:GEMINI_MODEL="gemini-2.5-flash"
```

Gemini setup in macOS / Linux:

```bash
export LLM_PROVIDER="gemini"
export GEMINI_API_KEY="your_gemini_api_key_here"
export GEMINI_MODEL="gemini-2.5-flash"
```

Optional Groq setup:

```powershell
$env:LLM_PROVIDER="groq"
$env:GROQ_API_KEY="your_groq_api_key_here"
$env:GROQ_MODEL="llama-3.3-70b-versatile"
```

Optional Groq setup in macOS / Linux:

```bash
export LLM_PROVIDER="groq"
export GROQ_API_KEY="your_groq_api_key_here"
export GROQ_MODEL="llama-3.3-70b-versatile"
```

## Running the project

### Streamlit UI

```bash
streamlit run frontend/app.py
```

The UI provides:

- Contract upload or pasted source input
- One-click loading of built-in demo contracts
- Preferred LLM selection between Gemini and Groq
- Mythril fallback toggle with hover explanation
- Cleaner report-style finding cards
- Severity breakdown summary
- Download buttons for JSON, HTML, and PDF

### FastAPI backend

```bash
uvicorn backend.main:app --reload --port 8001
```

Default local URL:

```text
http://127.0.0.1:8001
```

Available endpoints:

- `GET /health`
- `POST /analyze/text`
- `POST /analyze/file` if `python-multipart` is installed

If you want `/analyze/file` support:

```bash
pip install python-multipart
```

### Example API request

```bash
curl -X POST "http://127.0.0.1:8001/analyze/text" \
  -H "Content-Type: application/json" \
  -d "{\"contract_name\":\"Demo\",\"source_code\":\"pragma solidity ^0.8.20; contract Demo { uint256 public value; }\"}"
```

## Sample contracts included

### Vulnerable examples

- `reentrancy_vulnerable.sol`
- `access_control_vulnerable.sol`
- `tx_origin_vulnerable.sol`
- `timestamp_lottery_vulnerable.sol`
- `selfdestruct_vulnerable.sol`

### Safer comparison examples

- `safe_vault.sol`
- `safe_access_vault.sol`
- `safe_time_lock.sol`

### Extra legacy sample

- `integer_overflow_legacy.sol`

Note:
This legacy sample uses an older compiler range and may require matching compiler support on your machine.

## Example output shape

```json
{
  "vulnerability": "Reentrancy",
  "severity": "High",
  "category": "State management",
  "location": "reentrancy_vulnerable.sol:11 (withdraw)",
  "description": "Reentrancy in ReentrancyVulnerable.withdraw(uint256)",
  "simple_explanation": "This function makes an external call before it finishes updating internal state.",
  "exploit_scenario": [
    "The attacker becomes eligible to withdraw funds.",
    "The vulnerable function sends ETH before reducing the attacker's balance.",
    "The attacker re-enters before state is updated."
  ],
  "impact": "Contract funds can be drained.",
  "fix_recommendation": "Apply Checks-Effects-Interactions and use a reentrancy guard."
}
```

## Troubleshooting

### Streamlit says `No module named 'backend'`

Run it from the project root:

```bash
streamlit run frontend/app.py
```

### FastAPI says `python-multipart` is missing

Install it if you want `/analyze/file` support:

```bash
pip install python-multipart
```

### Slither fails to compile a contract

Check:

```bash
slither --version
solc --version
```

Common causes:

- Solidity compiler not installed
- Contract pragma not matching available compiler version
- Missing imports in a multi-file contract

### Mythril fallback behavior

The `Use Mythril fallback` option runs a second scan pass after Slither using Mythril.

- It is helpful when you want an extra analysis pass from a different engine.
- It can increase scan time.
- It may add extra findings that need manual review because they can be noisier than Slither output.

### Pasted JSON does not analyze

The analyzer expects Solidity source code, not example report JSON.

## Suggested demo flow

1. Start the Streamlit app.
2. Set `LLM_PROVIDER=gemini` and `GEMINI_API_KEY`.
3. Upload `samples/reentrancy_vulnerable.sol`.
4. Show the severity summary and readable finding card.
5. Compare it with `samples/safe_vault.sol`.
6. Export the report as HTML or PDF.

## Important limitations

- Static analyzers do not prove exploitability.
- The app filters low-value informational noise, so not every analyzer message is shown in the main report.
- Real smart contract audits still require human review.
- AI-generated explanations improve readability, but they still need validation.
