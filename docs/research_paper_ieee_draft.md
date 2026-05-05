# AI Smart Contract Risk Explainer: An IEEE-Style Research Paper Draft

Author Name  
Department of Computer Science / Cyber Security  
University Name, City, Country  
email@example.com

## Abstract
Smart contracts deployed on Ethereum and similar blockchain platforms automate financial and governance logic without requiring centralized control. However, once deployed, these programs are difficult to modify and may directly control valuable digital assets, making implementation errors highly expensive. Common vulnerabilities such as reentrancy, access control flaws, unsafe external calls, and misuse of blockchain-dependent values have repeatedly caused financial losses and protocol failures. This paper presents the design and implementation of AI Smart Contract Risk Explainer, a lightweight security analysis system that combines static analysis with large language model based explanation. The system accepts Solidity source code, analyzes it using Slither as the primary detector and Mythril as an optional fallback pass, normalizes the raw findings into structured vulnerability records, and generates plain-English explanations that describe the vulnerability, exploit path, impact, and remediation guidance. A Streamlit-based user interface presents findings as a readable security report and supports JSON, HTML, and PDF export. The contribution of the project is not the replacement of expert audits, but the addition of explainability and reporting on top of automated detection. The resulting system is useful for academic demonstration, developer education, and early-stage security review workflows.

Index Terms—smart contracts, Solidity, blockchain security, static analysis, vulnerability detection, large language models, explainable AI, Ethereum

## I. INTRODUCTION
Blockchain platforms such as Ethereum introduced programmable assets through smart contracts, allowing developers to encode business logic directly into decentralized applications [1]. This capability enabled decentralized finance, token ecosystems, governance protocols, and digital ownership models. At the same time, the security surface of blockchain software expanded. Unlike conventional web applications, smart contracts frequently execute irreversible financial operations, expose public entry points, and operate under deterministic runtime constraints. Vulnerabilities in these contracts can therefore lead to immediate financial damage, service disruption, or permanent loss of control.

The history of blockchain security shows that smart contract bugs are not theoretical edge cases. Reentrancy attacks, improper authorization, logic flaws in external calls, and trust in manipulable on-chain values have repeatedly resulted in protocol compromise. Although mature static analyzers exist, their output is often difficult for students and non-specialist developers to interpret. Raw detector names and machine-generated descriptions may identify risky patterns, but they do not always explain why a pattern is dangerous, how an attacker would exploit it, and what remediation strategy should be applied.

This project addresses that gap by combining vulnerability detection with explainable reporting. The proposed system, AI Smart Contract Risk Explainer, accepts Solidity source code, analyzes it through automated tools, transforms the analyzer output into normalized findings, and then generates security explanations using a configurable large language model layer. The system is intended as an assistive analysis tool rather than a replacement for expert auditing. Its goal is to improve understanding, accelerate triage, and produce better project documentation for academic and development environments.

## II. PROBLEM STATEMENT AND OBJECTIVES
The core problem addressed by this work is the limited usability of raw automated smart contract analysis results. Existing static analyzers can detect known patterns efficiently, but their output is often too low level for project demonstrations, student submissions, or rapid decision-making by non-specialists. A detector may indicate the existence of reentrancy or a suspicious authorization pattern, yet a developer still needs to understand the exploit sequence, the impact on assets or state, and the appropriate fix.

The primary objective of the proposed system is therefore to build a practical pipeline that combines detection and explanation. The specific objectives are:

- to accept Solidity code from direct input or file upload,
- to detect vulnerabilities using Slither and optionally Mythril,
- to normalize findings into a structured intermediate representation,
- to explain each finding in clear plain English,
- to provide remediation guidance with fix-oriented snippets when possible, and
- to generate a readable report suitable for both demonstration and documentation.

These objectives are intentionally scoped for a practical student project. The system does not attempt to build a formal verifier, simulate all economic behaviors, or train a domain-specific model from scratch. Instead, it focuses on a realistic and defensible security workflow that combines established static analysis with an explanation layer.

## III. RELATED WORK
Ethereum smart contract security has been studied extensively because deployed contracts often manage assets under adversarial conditions. The Ethereum white paper established the conceptual foundation for programmable decentralized applications, but later work made clear that expressiveness also introduces significant risk [1]. Solidity itself provides a contract-oriented language for Ethereum development, and its documentation emphasizes the importance of secure patterns, compiler behavior, and explicit handling of low-level operations [2].

Among practical security tools, Slither is one of the most widely used static analysis frameworks for Solidity. Feist, Grieco, and Groce describe Slither as a fast and extensible framework that converts Solidity code into an intermediate representation called SlithIR and supports vulnerability detection, code understanding, and audit assistance [3]. Slither is especially appropriate for educational and engineering use because of its speed and broad detector support.

Mythril represents another important class of smart contract security tool. It operates through symbolic analysis of EVM bytecode and can uncover issues from a different analysis perspective than source-oriented static detectors. Survey literature around Mythril highlights its usefulness for identifying security weaknesses while also noting the tradeoff of heavier analysis cost and possible reporting noise in some contexts [4].

Recent progress in large language models provides an opportunity to augment traditional security tools with explanation, summarization, and remediation guidance. API-accessible models such as Gemini and Groq-hosted models can be used as reasoning layers that transform structured findings into human-readable security narratives [5], [6]. However, LLM output should be treated as assistive rather than authoritative. This project therefore uses LLMs only after structured analysis has already identified concrete technical findings.

## IV. PROPOSED SYSTEM DESIGN
The proposed system follows a staged pipeline in which each component performs a narrow and well-defined responsibility. This separation improves clarity, maintainability, and extensibility.

### A. Input Layer
The system accepts either an uploaded Solidity file or pasted source code. Input validation ensures that the payload resembles Solidity rather than arbitrary text or previously generated report JSON. This check prevents unnecessary analyzer failures and improves the user experience.

### B. Static Analysis Layer
Slither is used as the primary detector because it is fast, widely adopted, and particularly effective for source-level Solidity analysis [3]. The tool is executed against a temporary copy of the submitted contract. Mythril is exposed as an optional fallback pass. When enabled, it performs a second scan intended to complement Slither with a different analysis approach.

### C. Parsing and Normalization Layer
Raw analyzer output is converted into a structured internal model. The parser removes low-signal informational noise, maps detector identifiers into more readable vulnerability titles, assigns severity categories, extracts source locations, and captures nearby code snippets. The result is a normalized finding format that is stable for API output, UI rendering, and report generation.

### D. AI Explanation Layer
After detection and normalization, each finding is passed to an explanation engine. The engine uses a provider abstraction that supports Gemini as the preferred model and Groq as a secondary option. If no external API provider is configured, a built-in rule-based explanation path is used. For each finding, the engine produces a simple explanation, exploit scenario, impact statement, and fix recommendation.

### E. Report and Presentation Layer
The final report is presented through a Streamlit interface and can also be exported as JSON, HTML, and PDF. The frontend emphasizes severity, vulnerability category, source location, impact, and remediation instead of exposing raw analyzer text by default. This makes the output suitable for demonstrations, project reports, and introductory security review.

## V. SYSTEM ARCHITECTURE
The architecture is organized into modular backend and frontend layers. The backend is implemented in Python and exposes a FastAPI application for programmatic access. The frontend is built in Streamlit for rapid prototyping and demonstration. The primary backend modules are:

- `analyzer.py` for invoking Slither and Mythril,
- `parser.py` for converting tool output into normalized findings,
- `ai_engine.py` for Gemini or Groq based explanation generation,
- `report.py` for summary and export generation, and
- `main.py` for orchestration and API routes.

The frontend consumes the same backend analysis path used by the API and renders findings as report-style cards. Sample vulnerable and safer contracts are included in the repository to support repeatable testing of common vulnerability classes such as reentrancy, access control weaknesses, timestamp dependence, `tx.origin` misuse, and unsafe destructive behavior.

## VI. IMPLEMENTATION DETAILS
The project was implemented in Python to simplify integration with command-line security tools and modern API SDKs. The backend uses structured models to ensure consistent report output across the API, UI, and exports. A validation step checks that the submitted input appears to be Solidity source code. This avoids user confusion caused by submitting example JSON or incompatible text into the analyzer path.

The Slither parser was refined to improve readability. Raw detector names are translated into clearer labels such as Reentrancy, `tx.origin` Authentication, or Timestamp Dependence. Informational-only findings that create report clutter are filtered from the main output. Nearby code snippets are extracted using source line numbers to help the user understand the context of each finding without manually searching the contract.

The explanation engine is designed around a provider abstraction rather than hard-coding a single model backend. Gemini is used as the preferred provider in the current version of the project, while Groq remains available as a secondary option. This design keeps the project flexible and reduces lock-in to a single API vendor. When an external provider is not configured, rule-based explanations preserve usability and allow the system to function in offline or limited environments.

The frontend was also intentionally simplified. Instead of displaying every raw analyzer field, it emphasizes severity metrics, finding summaries, exploit flow, impact, and remediation. Mythril is presented as an optional fallback with a hover explanation describing its purpose and tradeoffs. Built-in sample contracts can be loaded through friendly labels instead of raw file names, which improves usability during demonstrations.

## VII. EXPERIMENTAL SETUP AND TEST CONTRACTS
The system was evaluated using a curated set of Solidity samples included in the repository. The vulnerable set contains contracts representing:

- reentrancy through external calls before state updates,
- missing or weak access control,
- `tx.origin` based authorization,
- timestamp-dependent lottery logic, and
- unprotected destructive contract behavior.

The repository also contains safer comparison contracts intended to reduce or eliminate those same high-signal issues. This curated sample approach does not claim benchmark-level coverage, but it is appropriate for validating the end-to-end behavior of the prototype.

The evaluation process followed a simple sequence. Each sample contract was submitted to the system through the frontend or backend route. Slither findings were captured and normalized. Where enabled, Mythril acted as an additional scan pass. Finally, the explanation layer generated readable descriptions of the findings. The success criterion was not numerical benchmark dominance, but the consistent production of meaningful and understandable reports for vulnerable contracts while producing substantially cleaner output for safer contracts.

## VIII. RESULTS AND DISCUSSION
The prototype successfully demonstrates the intended value of combining static analysis with explainable reporting. Vulnerable samples produced structured findings aligned with expected classes such as reentrancy, authorization flaws, and timestamp dependence. The safer comparison contracts produced fewer or no high-signal findings after parser-level filtering. This is important because it shows that the system is not merely amplifying detector output, but is actively shaping it into a more usable artifact.

The most significant benefit of the system is readability. Raw security tool output can be intimidating or opaque for students and early-stage developers. By contrast, the generated report highlights what the issue is, how it could be exploited, what damage may result, and how to fix it. This improves the educational value of the tool and makes it more suitable for classroom projects, presentations, and initial development review.

The multi-provider explanation layer also adds practical flexibility. Gemini offers a direct path for explanation generation through Google’s current SDK, while Groq provides an additional option when preferred by the user. The provider abstraction keeps the design maintainable and separates model choice from the rest of the analysis pipeline.

However, the results must be interpreted carefully. Static analysis tools detect patterns, not guaranteed exploitability. Likewise, generated explanations can make reasoning more accessible, but they do not replace expert validation. The system is therefore best understood as an intelligent triage and explanation assistant.

## IX. THREATS TO VALIDITY AND LIMITATIONS
Several limitations affect the generality of this prototype. First, the current evaluation uses a curated repository sample set rather than a large public benchmark corpus. This is sufficient for project demonstration, but it does not support strong claims about general detection accuracy, false positive rates, or performance at scale.

Second, the project relies heavily on external analyzers and model APIs. Changes in tool versions, compiler configuration, or API behavior may affect reproducibility. Solidity compiler compatibility remains a practical constraint, particularly for older sample contracts or multi-file projects with version-specific dependencies.

Third, the explanation layer can improve clarity while still introducing risk if its output is accepted uncritically. LLM-generated remediation guidance may be plausible but incomplete, and subtle contract semantics may still require expert review. For this reason, the system should be positioned as assistive infrastructure, not an autonomous auditor.

Finally, the current system focuses on contract-level source submissions rather than full protocol ecosystems. Economic exploits, cross-contract assumptions, and complex governance interactions often require deeper manual reasoning than this prototype currently provides.

## X. CONCLUSION AND FUTURE WORK
This paper presented AI Smart Contract Risk Explainer, a lightweight smart contract security analysis system that combines Slither-based detection, optional Mythril fallback analysis, structured finding normalization, and LLM-supported explanation generation. The system demonstrates that the practical value of automated analysis can be increased significantly when technical findings are transformed into readable, structured security reports. The resulting prototype is appropriate for academic demonstration, early-stage developer review, and educational use in blockchain security projects.

Future work can strengthen the project in several directions. First, the evaluation set can be expanded to include public benchmark contracts and multi-file real-world projects. Second, snippet extraction and remediation suggestions can be made more context aware. Third, report generation can be extended with richer tables, comparative analyzer output, and stored scan history. Finally, deeper integration with formal verification or symbolic execution workflows could improve coverage for complex logic and protocol-level reasoning.

## Acknowledgment
This draft is intended as a project research paper template and can be adapted with actual author names, institution details, experimental results, and supervisor acknowledgment before submission.

## References
[1] V. Buterin, “A Next-Generation Smart Contract and Decentralized Application Platform,” Ethereum White Paper, 2014.

[2] Solidity Team, “Solidity Documentation,” Soliditylang.org. [Online]. Available: https://docs.soliditylang.org/

[3] J. Feist, G. Grieco, and A. Groce, “Slither: A Static Analysis Framework for Smart Contracts,” in 2019 IEEE/ACM 2nd International Workshop on Emerging Trends in Software Engineering for Blockchain (WETSEB), Montreal, QC, Canada, 2019, pp. 8–15, doi: 10.1109/WETSEB.2019.00008.

[4] N. Sharma and S. Sharma, “A Survey of Mythril, A Smart Contract Security Analysis Tool for EVM Bytecode,” Indian Journal of Natural Sciences, vol. 13, no. 75, Dec. 2022.

[5] Google AI for Developers, “Gemini API Documentation.” [Online]. Available: https://ai.google.dev/gemini-api/docs

[6] Groq, “Groq API Documentation.” [Online]. Available: https://console.groq.com/docs/
