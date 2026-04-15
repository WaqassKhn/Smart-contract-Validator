# ETHBlockchain Project Explanation

## What this project is

This project is an **AI Smart Contract Risk Explainer**.

Its job is to help a user understand security problems in Solidity smart contracts.

It does that by combining:

1. static analysis tools,
2. Python backend code,
3. an AI explanation layer,
4. a simple frontend,
5. downloadable reports.

In plain language, this project reads smart contract code, looks for possible security issues, and explains those issues in easier words.

## Important beginner definitions

If you are completely new to this topic, start here.

- **Ethereum**: a blockchain platform where programs can run.
- **Smart contract**: a program deployed on a blockchain.
- **Solidity**: the language used to write most Ethereum smart contracts.
- **Static analyzer**: a tool that checks source code without running it.
- **Vulnerability**: a security weakness that an attacker might abuse.
- **Finding**: one warning or issue reported by an analyzer.
- **Reentrancy**: a bug where a contract calls external code before safely updating its own data.
- **Access control**: the rules that decide who is allowed to do sensitive actions.
- **Overflow**: when a number becomes larger than the type can safely hold.
- **Report**: the final result shown to the user after analysis.

## High-level purpose

The project is built for a blockchain and cyber security academic demo.

It is meant to solve a practical problem:

Security tools often produce technical output that beginners struggle to understand.

This project tries to bridge that gap by:

- scanning the contract,
- normalizing the results,
- explaining the issues in simple language,
- showing impact and fixes,
- exporting the result in useful formats.

## Project structure

The current repository has these major parts:

- [README.md](I:\SeM_6\CS&BC\ETHBlockchain\README.md)
- [requirements.txt](I:\SeM_6\CS&BC\ETHBlockchain\requirements.txt)
- [backend/__init__.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\__init__.py)
- [backend/models.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\models.py)
- [backend/analyzer.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\analyzer.py)
- [backend/parser.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\parser.py)
- [backend/ai_engine.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\ai_engine.py)
- [backend/report.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\report.py)
- [backend/main.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\main.py)
- [frontend/app.py](I:\SeM_6\CS&BC\ETHBlockchain\frontend\app.py)
- sample contracts and a sample report in [samples](I:\SeM_6\CS&BC\ETHBlockchain\samples)

## What each part does

### Root files

- [README.md](I:\SeM_6\CS&BC\ETHBlockchain\README.md): short project overview, setup, and run instructions.
- [requirements.txt](I:\SeM_6\CS&BC\ETHBlockchain\requirements.txt): Python packages required by the project.
- [.gitignore](I:\SeM_6\CS&BC\ETHBlockchain\.gitignore): files that should not be committed, such as virtual environments and generated reports.

### Backend folder

The backend is the core of the system.

It contains:

- data models,
- analyzer wrappers,
- parser logic,
- AI explanation logic,
- report generation,
- API endpoints.

### Frontend folder

The frontend contains the Streamlit application that the user interacts with.

### Samples folder

The samples folder contains example Solidity contracts and one example report.

These files help the user test and understand the system.

## Dependency meaning

The packages in [requirements.txt](I:\SeM_6\CS&BC\ETHBlockchain\requirements.txt) reveal the system design.

- `fastapi`: builds the backend HTTP API.
- `uvicorn`: runs the FastAPI app.
- `streamlit`: builds the web UI quickly.
- `pydantic`: validates and structures Python data.
- `openai`: generates AI-assisted explanations.
- `reportlab`: creates PDF reports.
- `python-multipart`: supports uploaded files in forms.

## End-to-end workflow

The full project flow works like this:

1. The user uploads a Solidity file or pastes Solidity code in the frontend.
2. The frontend builds an `AnalysisTarget` object.
3. The backend writes the contract into a temporary `.sol` file.
4. Slither analyzes that file.
5. Mythril may also analyze it if the user enables the option.
6. The parser converts raw analyzer output into normalized findings.
7. The AI engine explains each finding in simpler language.
8. The backend builds a final `AnalysisReport`.
9. The frontend displays the findings.
10. The user can download JSON, HTML, or PDF reports.

## The most important backend concepts

The backend is organized so each file does one main job.

- `models.py`: defines what the data looks like.
- `analyzer.py`: talks to external security tools.
- `parser.py`: converts tool output into clean objects.
- `ai_engine.py`: generates explanations for humans.
- `report.py`: converts the result into report formats.
- `main.py`: connects everything into one working pipeline.

## File-by-file explanation

### [backend/__init__.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\__init__.py)

This file only marks the folder as a Python package.

It contains a short package description and no real logic.

### [backend/models.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\models.py)

This file defines the data structures used everywhere else.

#### `AnalysisTarget`

Reference: [backend/models.py:8](I:\SeM_6\CS&BC\ETHBlockchain\backend\models.py#L8)

Purpose:
Represents the contract that will be analyzed.

Fields:

- `contract_name`
- `source_code`
- `filename`

Use in the project:
This is the main input object passed into the analysis pipeline.

#### `VulnerabilityFinding`

Reference: [backend/models.py:14](I:\SeM_6\CS&BC\ETHBlockchain\backend\models.py#L14)

Purpose:
Represents one normalized vulnerability result.

Important fields:

- `vulnerability`
- `severity`
- `confidence`
- `location`
- `function`
- `description`
- `detector`
- `code_snippet`
- `tool`
- `raw`

Use in the project:
This is the shared internal format used after parsing analyzer output.

#### `ExplainedFinding`

Reference: [backend/models.py:27](I:\SeM_6\CS&BC\ETHBlockchain\backend\models.py#L27)

Purpose:
Adds human-friendly explanation fields on top of `VulnerabilityFinding`.

Extra fields:

- `simple_explanation`
- `exploit_scenario`
- `impact`
- `fix_recommendation`
- `corrected_code`

Use in the project:
This is the format used when results are ready for a human reader.

#### `AnalysisReport`

Reference: [backend/models.py:35](I:\SeM_6\CS&BC\ETHBlockchain\backend\models.py#L35)

Purpose:
Represents the full final analysis result.

Fields:

- `contract_name`
- `source`
- `finding_count`
- `findings`
- `summary`
- `tool_status`

Use in the project:
This is the final object returned by the backend and displayed in the frontend.

### [backend/analyzer.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\analyzer.py)

This file is responsible for running external tools.

#### `AnalyzerError`

Reference: [backend/analyzer.py:12](I:\SeM_6\CS&BC\ETHBlockchain\backend\analyzer.py#L12)

Purpose:
Signals that an analyzer failed to run correctly.

#### `_write_temp_contract(target)`

Reference: [backend/analyzer.py:16](I:\SeM_6\CS&BC\ETHBlockchain\backend\analyzer.py#L16)

Purpose:
Writes the uploaded contract source code to a temporary file.

Why it exists:
Slither and Mythril work on files, not raw strings.

Input:
- `AnalysisTarget`

Output:
- a temporary file path

#### `_run_command(command, cwd=None)`

Reference: [backend/analyzer.py:24](I:\SeM_6\CS&BC\ETHBlockchain\backend\analyzer.py#L24)

Purpose:
Runs a subprocess command and captures output.

Why it exists:
It prevents duplicate subprocess code inside analyzer functions.

#### `run_slither(target)`

Reference: [backend/analyzer.py:34](I:\SeM_6\CS&BC\ETHBlockchain\backend\analyzer.py#L34)

Purpose:
Runs Slither on a contract.

Detailed behavior:

1. checks that `slither` exists,
2. writes the contract to a temp file,
3. runs `slither <file> --json -`,
4. parses the JSON output,
5. returns the raw payload and status metadata.

Important note:
This function raises `AnalyzerError` when Slither is missing or invalid.

#### `run_mythril(target)`

Reference: [backend/analyzer.py:59](I:\SeM_6\CS&BC\ETHBlockchain\backend\analyzer.py#L59)

Purpose:
Runs Mythril on a contract.

Detailed behavior:

1. checks whether `myth` is installed,
2. writes the contract to a temp file,
3. runs Mythril in JSON mode,
4. parses the output when possible,
5. returns results or a status message.

Difference from Slither:
This function is more forgiving and can return `None` instead of raising.

### [backend/parser.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\parser.py)

This file converts raw tool output into a standard project format.

#### `SEVERITY_MAP`

Reference: [backend/parser.py:8](I:\SeM_6\CS&BC\ETHBlockchain\backend\parser.py#L8)

Purpose:
Maps analyzer severities into a simpler project severity scale.

#### `KEYWORD_SEVERITY`

Reference: [backend/parser.py:17](I:\SeM_6\CS&BC\ETHBlockchain\backend\parser.py#L17)

Purpose:
Provides fallback severity guesses based on vulnerability keywords.

#### `_guess_severity(check, impact)`

Reference: [backend/parser.py:32](I:\SeM_6\CS&BC\ETHBlockchain\backend\parser.py#L32)

Purpose:
Determines severity for a finding.

How it works:

- use known analyzer impact if available,
- otherwise inspect the issue name,
- otherwise default to `"Medium"`.

#### `_extract_location(element)`

Reference: [backend/parser.py:43](I:\SeM_6\CS&BC\ETHBlockchain\backend\parser.py#L43)

Purpose:
Builds a readable location string such as file name, line number, and function name.

Why it matters:
Users need to know where the problem exists.

#### `parse_slither_output(payload)`

Reference: [backend/parser.py:59](I:\SeM_6\CS&BC\ETHBlockchain\backend\parser.py#L59)

Purpose:
Converts Slither JSON into a list of `VulnerabilityFinding` objects.

What it does:

1. reads detector entries,
2. extracts a main location,
3. creates standardized findings,
4. returns a clean list for later steps.

#### `parse_mythril_output(payload)`

Reference: [backend/parser.py:87](I:\SeM_6\CS&BC\ETHBlockchain\backend\parser.py#L87)

Purpose:
Converts Mythril JSON into the same shared finding format.

Why it matters:
The rest of the project can handle both tools in one common format.

### [backend/ai_engine.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\ai_engine.py)

This file explains security findings in language a learner can understand.

#### `PROMPT_TEMPLATE`

Reference: [backend/ai_engine.py:11](I:\SeM_6\CS&BC\ETHBlockchain\backend\ai_engine.py#L11)

Purpose:
Defines the prompt sent to the OpenAI API.

It asks for:

- a simple explanation,
- an exploit scenario,
- likely impact,
- a fix recommendation,
- corrected code when possible.

#### `RULE_BASED_EXPLANATIONS`

Reference: [backend/ai_engine.py:34](I:\SeM_6\CS&BC\ETHBlockchain\backend\ai_engine.py#L34)

Purpose:
Stores built-in fallback explanations for common issues.

Examples covered:

- reentrancy,
- access control,
- integer overflow.

Why it matters:
The project still works even without an API key.

#### `_rule_based_response(finding)`

Reference: [backend/ai_engine.py:74](I:\SeM_6\CS&BC\ETHBlockchain\backend\ai_engine.py#L74)

Purpose:
Creates an `ExplainedFinding` using only local rule-based templates.

When it is used:

- when no OpenAI key exists,
- when the API output cannot be parsed,
- when the project falls back to safe built-in explanations.

#### `_openai_response(finding)`

Reference: [backend/ai_engine.py:98](I:\SeM_6\CS&BC\ETHBlockchain\backend\ai_engine.py#L98)

Purpose:
Calls OpenAI to generate a richer explanation for a finding.

How it works:

1. reads `OPENAI_API_KEY`,
2. falls back to rules if the key is missing,
3. creates the prompt,
4. calls `client.responses.create(...)`,
5. parses the JSON output,
6. falls back to rules if parsing fails.

Why it matters:
This is the main AI feature in the project.

#### `explain_finding(finding)`

Reference: [backend/ai_engine.py:133](I:\SeM_6\CS&BC\ETHBlockchain\backend\ai_engine.py#L133)

Purpose:
Public helper for explaining one finding.

#### `explain_findings(findings)`

Reference: [backend/ai_engine.py:137](I:\SeM_6\CS&BC\ETHBlockchain\backend\ai_engine.py#L137)

Purpose:
Loops over a list of findings and explains each one.

### [backend/report.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\report.py)

This file prepares the final output formats.

#### `build_summary(report)`

Reference: [backend/report.py:9](I:\SeM_6\CS&BC\ETHBlockchain\backend\report.py#L9)

Purpose:
Creates a short summary sentence for the top of the report.

#### `report_to_json(report)`

Reference: [backend/report.py:18](I:\SeM_6\CS&BC\ETHBlockchain\backend\report.py#L18)

Purpose:
Converts the report object into JSON text.

#### `report_to_html(report)`

Reference: [backend/report.py:22](I:\SeM_6\CS&BC\ETHBlockchain\backend\report.py#L22)

Purpose:
Builds an HTML report containing each finding and its explanation.

What it shows:

- severity,
- location,
- description,
- explanation,
- exploit steps,
- impact,
- fix recommendation,
- corrected code.

#### `save_html_report(report, destination)`

Reference: [backend/report.py:90](I:\SeM_6\CS&BC\ETHBlockchain\backend\report.py#L90)

Purpose:
Writes the HTML output to disk.

#### `save_json_report(report, destination)`

Reference: [backend/report.py:96](I:\SeM_6\CS&BC\ETHBlockchain\backend\report.py#L96)

Purpose:
Writes the JSON output to disk.

#### `save_pdf_report(report, destination)`

Reference: [backend/report.py:102](I:\SeM_6\CS&BC\ETHBlockchain\backend\report.py#L102)

Purpose:
Creates a PDF report using ReportLab.

Why it matters:
This gives the user a shareable offline version of the analysis.

### [backend/main.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\main.py)

This file is the most important integration layer in the backend.

#### `app = FastAPI(...)`

Reference: [backend/main.py:10](I:\SeM_6\CS&BC\ETHBlockchain\backend\main.py#L10)

Purpose:
Creates the FastAPI application.

#### `analyze_contract(target, use_mythril=False)`

Reference: [backend/main.py:13](I:\SeM_6\CS&BC\ETHBlockchain\backend\main.py#L13)

Purpose:
This is the central orchestration function.

Detailed flow:

1. call `run_slither`,
2. parse the Slither output,
3. optionally call `run_mythril`,
4. parse Mythril output,
5. explain all findings,
6. build an `AnalysisReport`,
7. generate the summary,
8. return the report.

If you want one function that represents the whole backend pipeline, this is the one.

#### `health()`

Reference: [backend/main.py:33](I:\SeM_6\CS&BC\ETHBlockchain\backend\main.py#L33)

Purpose:
Simple health endpoint for checking whether the backend is running.

Output:
- `{"status": "ok"}`

#### `analyze_text(payload, use_mythril=False)`

Reference: [backend/main.py:38](I:\SeM_6\CS&BC\ETHBlockchain\backend\main.py#L38)

Purpose:
API endpoint that accepts Solidity code as JSON text input.

#### `analyze_file(...)`

Reference: [backend/main.py:46](I:\SeM_6\CS&BC\ETHBlockchain\backend\main.py#L46)

Purpose:
API endpoint that accepts an uploaded Solidity file.

What it does:

1. reads the uploaded bytes,
2. decodes them to text,
3. creates an `AnalysisTarget`,
4. calls `analyze_contract`,
5. returns the final report.

### [frontend/app.py](I:\SeM_6\CS&BC\ETHBlockchain\frontend\app.py)

This file is the frontend UI built with Streamlit.

#### Page setup

Reference: [frontend/app.py:11](I:\SeM_6\CS&BC\ETHBlockchain\frontend\app.py#L11)

Purpose:
Sets the page title and layout, then shows the page title and caption.

#### `render_finding_card(finding)`

Reference: [frontend/app.py:17](I:\SeM_6\CS&BC\ETHBlockchain\frontend\app.py#L17)

Purpose:
Displays one finding in a user-friendly card.

What it shows:

- vulnerability title,
- severity,
- location,
- description,
- explanation,
- exploit scenario,
- impact,
- fix recommendation,
- corrected code if available.

This is important because it transforms technical output into a readable visual format.

#### Sidebar options

Reference: [frontend/app.py:40](I:\SeM_6\CS&BC\ETHBlockchain\frontend\app.py#L40)

Purpose:
Collects user settings such as:

- contract label,
- whether Mythril should run,
- requirement reminders.

#### Upload and text inputs

Reference: [frontend/app.py:51](I:\SeM_6\CS&BC\ETHBlockchain\frontend\app.py#L51)

Purpose:
Lets the user either upload a file or paste source code manually.

#### Main analyze button flow

Reference: [frontend/app.py:54](I:\SeM_6\CS&BC\ETHBlockchain\frontend\app.py#L54)

Purpose:
Runs the full frontend workflow.

Detailed behavior:

1. read uploaded content if present,
2. otherwise use pasted text,
3. validate that contract code exists,
4. call `analyze_contract`,
5. show success or error messages,
6. render findings,
7. generate JSON and HTML downloads,
8. try to generate a PDF file and offer it as a download.

## Sample contracts explained

### [samples/access_control_vulnerable.sol](I:\SeM_6\CS&BC\ETHBlockchain\samples\access_control_vulnerable.sol)

Purpose:
Shows a contract with missing authorization.

What is vulnerable:

- anyone can call `transferOwnership`,
- anyone can call `emergencyWithdraw`.

Meaning:
An attacker could take control or move funds.

### [samples/reentrancy_vulnerable.sol](I:\SeM_6\CS&BC\ETHBlockchain\samples\reentrancy_vulnerable.sol)

Purpose:
Shows a classic reentrancy bug.

What is vulnerable:

- ETH is sent before the internal balance is reduced.

Meaning:
An attacker can call back into `withdraw` before the first withdrawal finishes.

### [samples/integer_overflow_legacy.sol](I:\SeM_6\CS&BC\ETHBlockchain\samples\integer_overflow_legacy.sol)

Purpose:
Shows a legacy overflow example in Solidity `0.7.6`.

What is vulnerable:

- `uint8 counter = 255`,
- `counter += 1` can wrap around in older Solidity behavior.

Meaning:
The value can become incorrect because the number type is too small.

### [samples/safe_vault.sol](I:\SeM_6\CS&BC\ETHBlockchain\samples\safe_vault.sol)

Purpose:
Shows a safer pattern for comparison.

Why it is safer:

- `onlyOwner` protects the rescue function,
- balance is reduced before funds are transferred.

### [samples/sample_report.json](I:\SeM_6\CS&BC\ETHBlockchain\samples\sample_report.json)

Purpose:
Shows what a final report looks like after analysis.

Why it matters:
This helps a beginner understand the shape of the output even before running the app.

## How the parts connect

Here is the low-level connection between components:

1. [frontend/app.py](I:\SeM_6\CS&BC\ETHBlockchain\frontend\app.py) collects user input.
2. It creates an `AnalysisTarget` from [backend/models.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\models.py).
3. [backend/main.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\main.py) calls the analyzer layer.
4. [backend/analyzer.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\analyzer.py) runs Slither and optional Mythril.
5. [backend/parser.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\parser.py) normalizes the output.
6. [backend/ai_engine.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\ai_engine.py) explains each finding.
7. [backend/report.py](I:\SeM_6\CS&BC\ETHBlockchain\backend\report.py) builds exports.
8. The frontend shows the report and enables downloads.

## What the end user should remember

If you remember only one thing, remember this:

This project is a teaching and demo tool that helps people understand smart contract vulnerabilities. It does not replace a real manual security audit, but it makes scanner results easier to read and learn from.

## Current limitations

The project already has a full prototype flow, but it still has clear limits:

- there are no automated tests,
- temporary analysis files are created without cleanup,
- the frontend directly imports backend functions instead of calling the FastAPI server over HTTP,
- report HTML is built by string formatting and could be hardened,
- results from different analyzers are not deduplicated,
- AI explanations are helpful but should still be verified by a human.

## Short project summary

This repository contains a Python-based prototype for analyzing Solidity smart contracts. The backend runs Slither and optional Mythril, parses the results, explains them using OpenAI or rule-based fallbacks, and builds reports. The frontend lets a user upload or paste contracts and download the analysis in multiple formats.
