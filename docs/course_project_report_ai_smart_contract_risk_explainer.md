# Course Project Report

## Cover Page

Course Project Report on  
**"AI Smart Contract Risk Explainer"**

Submitted in partial fulfillment of the requirements for the degree of  
**Bachelor of Technology**

in  
**Computer Science / Cyber Security / Blockchain**

Prepared by:
- Student Name 1 (Roll Number)
- Student Name 2 (Roll Number)
- Student Name 3 (Roll Number)
- Student Name 4 (Roll Number)

Under the guidance of:
- Guide Name

Department:
- Department Name

Institute:
- Institute Name

Academic Year:
- 2025-2026

## Certificate

This is to certify that the course project titled **"AI Smart Contract Risk Explainer"** submitted by the above students is a bonafide record of work carried out under the guidance of the undersigned in partial fulfillment of the requirements for the award of the Bachelor of Technology degree during the academic year 2025-2026.

Guide Signature: ____________________

Head of Department Signature: ____________________

Place: ____________________

Date: ____________________

## Project Synopsis

Project Title: **AI Smart Contract Risk Explainer**  
Project Area: **Blockchain Security, Smart Contract Analysis, Applied AI**  
Internal Guide: **Guide Name**  
Academic Year: **2025-2026**

### Abstract

AI Smart Contract Risk Explainer is a practical blockchain security project designed to analyze Solidity smart contracts, detect vulnerabilities using static analysis tools, and convert those technical findings into plain-English reports. The system uses Slither as the primary analyzer and Mythril as an optional fallback pass. It normalizes the analyzer output, categorizes issues by severity and type, and then uses a large language model based explanation layer to describe the vulnerability, possible exploit scenario, likely impact, and remediation guidance.

The project focuses on explainability rather than only detection. Its main contribution is that it helps students, developers, and evaluators understand not only *what* was detected, but also *why* it matters and *how* to fix it. The final system provides a Streamlit-based interface, structured export formats, and a curated set of vulnerable and safer sample contracts for demonstration and testing.

## Acknowledgement

We express our sincere gratitude to our project guide, faculty members, and department for their continuous support, guidance, and encouragement throughout the development of this project. We also acknowledge the contributions of the open-source security and blockchain communities whose tools and documentation made this work possible.

We are especially thankful for the availability of Solidity documentation, Ethereum references, Slither, Mythril, and modern AI model APIs, which helped us build a practical and educational security analysis workflow. Their availability significantly supported the successful completion of this project.

## Introduction

Smart contracts are self-executing programs deployed on blockchain platforms such as Ethereum. They enable decentralized finance, tokenized assets, digital governance, and other trust-minimized applications. However, because smart contracts often manage high-value assets and expose public functions to untrusted users, even small implementation flaws can lead to severe financial or operational loss.

Many smart contract vulnerabilities are difficult for new developers to understand from raw static analyzer output alone. Security tools may identify the presence of a reentrancy issue or unsafe external call pattern, but they do not always provide a beginner-friendly explanation of the exploit process or the corresponding fix. This creates a gap between detection and understanding.

AI Smart Contract Risk Explainer was developed to bridge this gap. It combines automated vulnerability detection with readable explanation and structured reporting so that security findings can be interpreted more effectively during development, review, and academic demonstration.

## Core Problem

Traditional static analyzers for smart contracts are useful but often difficult for non-specialists to interpret. Their output typically contains detector names, machine-oriented descriptions, and technical metadata that are meaningful to experienced auditors but less useful for students or early-stage developers.

The main problems addressed by this project are:

- difficulty in understanding raw vulnerability reports,
- lack of plain-English explanation of exploitability and impact,
- limited educational value of direct analyzer output,
- absence of an integrated lightweight reporting pipeline for academic demos.

## Objectives

The project was developed with the following objectives:

- to accept Solidity source code through upload or pasted input,
- to analyze the code using Slither as the primary detection engine,
- to optionally run Mythril as a secondary or fallback analysis pass,
- to convert raw analyzer results into structured vulnerability findings,
- to explain vulnerabilities in plain English,
- to generate readable JSON, HTML, and PDF style reports,
- to demonstrate the workflow through a simple frontend and curated sample contracts.

## Methodology

The implementation was carried out in multiple phases.

### Phase 1 – Analysis Pipeline Design

The initial phase focused on designing the overall security analysis pipeline. The backend was structured to:

- validate Solidity input,
- write the contract to a temporary analysis file,
- invoke Slither to scan for known vulnerability patterns,
- optionally invoke Mythril for a second analysis pass,
- collect raw scanner output into a standard internal format.

### Phase 2 – Parser and Report Normalization

The second phase focused on converting raw analyzer output into human-readable security findings. This included:

- filtering low-value informational noise,
- assigning normalized vulnerability names,
- grouping issues into categories such as access control, external calls, or state management,
- estimating severity from analyzer metadata,
- extracting nearby code snippets using source line information.

### Phase 3 – AI Explanation Layer

The third phase added the explanation engine. Gemini was configured as the preferred provider and Groq as an optional secondary provider. For each normalized finding, the system generates:

- a simple explanation,
- a likely exploit scenario,
- the expected impact,
- a remediation recommendation,
- and optionally a small corrected code snippet.

### Phase 4 – User Interface and Exports

The final phase focused on usability. A Streamlit frontend was built to:

- upload or paste Solidity contracts,
- load sample demonstration contracts,
- optionally enable Mythril fallback,
- choose the preferred LLM provider,
- display findings in a readable report-card style layout,
- and export results to JSON, HTML, and PDF.

## System Architecture

The project follows a modular Python-based architecture:

- **Frontend UI**: built in Streamlit for interaction and report viewing
- **Backend API / Orchestration**: built in FastAPI and Python
- **Static Analyzer Layer**: Slither as the primary engine, Mythril as optional fallback
- **Parser Layer**: converts raw tool output into structured normalized findings
- **AI Layer**: Gemini or Groq based explanation engine
- **Report Generator**: creates JSON, HTML, and PDF-ready outputs

### Architecture Flow

Frontend UI  
→ Backend Orchestration  
→ Static Analysis Layer  
→ Parser and Finding Normalization  
→ AI Explanation Layer  
→ Report Generator  
→ On-screen Report / Exported Files

## Component and Module Explanation

### 1. Analyzer Module

The analyzer module is responsible for invoking external security tools. It runs Slither as the main analyzer and handles command execution, return codes, and error messaging. It can also invoke Mythril when the fallback option is enabled.

### 2. Parser Module

The parser module interprets raw analyzer findings and transforms them into normalized vulnerability records. It removes unhelpful detector noise, maps technical detector names into readable labels, and extracts source location and surrounding code context.

### 3. AI Engine Module

The AI engine module receives structured findings and produces explanations. It supports Gemini as the preferred provider and Groq as a second option. If neither is configured, a rule-based fallback still generates useful educational output.

### 4. Report Module

The report module produces summaries and exports. It calculates severity breakdown, prepares HTML output, builds JSON responses, and supports PDF-style generation for project documentation or submission.

### 5. Frontend Module

The frontend provides the user-facing experience. It allows contract analysis without requiring command-line interaction and presents the results as readable security cards rather than raw tool dumps.

## Sample Contracts Used

The repository includes vulnerable and safer contracts to test the system:

### Vulnerable Samples

- reentrancy vulnerable contract
- access control vulnerable contract
- tx.origin vulnerable contract
- timestamp dependence vulnerable contract
- selfdestruct vulnerable contract

### Safer Comparison Samples

- safe vault contract
- safe access vault contract
- safe time lock contract

These samples help demonstrate both positive detection cases and cleaner outputs for contracts with stronger protections.

## Results

The completed prototype successfully demonstrates:

- detection of common smart contract vulnerability classes through Slither,
- optional fallback analysis using Mythril,
- structured normalization of findings,
- readable severity-based reporting,
- AI-generated explanation of exploit flow and impact,
- export support for JSON, HTML, and PDF outputs,
- educational comparison between vulnerable and safer contracts.

The system is especially useful in academic settings because it improves the readability of security findings while keeping the implementation lightweight and practical.

## Advantages of the Proposed System

- improves comprehension of static analyzer output,
- supports early-stage secure development practices,
- helps in project demonstration and evaluation,
- reduces dependence on manually interpreting raw detector output,
- integrates modern AI reasoning with conventional static analysis.

## Limitations

The current system has some practical limitations:

- it depends on the availability of external tools like Slither and optionally Mythril,
- it does not replace professional manual auditing,
- some advanced protocol-level or economic vulnerabilities may remain outside its scope,
- AI-generated explanation is assistive and must still be reviewed critically.

## Future Scope

The project can be extended in several directions:

- support for multi-file and multi-contract analysis,
- better snippet extraction and automatic patch suggestion,
- storage of historical reports and scan sessions,
- deeper comparative fusion of Slither and Mythril findings,
- support for additional security datasets and benchmark contracts,
- deployment as a shared internal web tool for teams or classrooms.

## Conclusion

AI Smart Contract Risk Explainer demonstrates that the practical usefulness of blockchain security tooling can be significantly improved when automated detection is combined with explanation and reporting. By integrating Slither, optional Mythril analysis, and an LLM-supported interpretation layer, the project transforms raw vulnerability output into an understandable and structured report.

The system does not attempt to replace expert smart contract audits. Instead, it serves as a strong educational and engineering aid that improves understanding, supports early-stage review, and makes vulnerability reporting more accessible. As a course project, it effectively demonstrates blockchain security knowledge, tool integration, applied AI usage, and practical software engineering.

## References

[1] V. Buterin, “A Next-Generation Smart Contract and Decentralized Application Platform,” Ethereum White Paper, 2014.

[2] Solidity Team, “Solidity Documentation,” Soliditylang.org. [Online]. Available: https://docs.soliditylang.org/

[3] J. Feist, G. Grieco, and A. Groce, “Slither: A Static Analysis Framework for Smart Contracts,” in 2019 IEEE/ACM 2nd International Workshop on Emerging Trends in Software Engineering for Blockchain (WETSEB), Montreal, QC, Canada, 2019, pp. 8–15.

[4] N. Sharma and S. Sharma, “A Survey of Mythril, A Smart Contract Security Analysis Tool for EVM Bytecode,” Indian Journal of Natural Sciences, vol. 13, no. 75, Dec. 2022.

[5] Google AI for Developers, “Gemini API Documentation.” [Online]. Available: https://ai.google.dev/gemini-api/docs

[6] Groq, “Groq API Documentation.” [Online]. Available: https://console.groq.com/docs/
