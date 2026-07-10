# prompt-craft: Tech Stack and Code Flow Guide

This document breaks down the technology stack and code execution flow for **prompt-craft** in detail.

---

## 1. The Technology Stack

prompt-craft is an interactive Python application served directly via Streamlit:

```
[ Developer Web Browser ] ◄──Port 8000 Connection──► [ Streamlit Runtime (app.py) ]
                                                            │
                                  ┌─────────────────────────┴─────────────────────────┐
                                  ▼                                                   ▼
                    [ Local Heuristics ]                                    [ Google Gemini Client ]
                    - Security Audit Regex                                  - few-shot optimization
                    - Assertion validators                                  - model benchmarking
```

### Core Technologies Used:
* **Streamlit (Python):** Renders the multi-tab layout, state controls, code editors, and tables dynamically in Python without JavaScript compilation.
* **Google Gemini API (google-genai SDK):** Connects to `gemini-2.5-flash` and `gemini-2.5-pro` to optimize prompts, generate synthetic training examples, and complete benchmarking runs.
* **Python RegEx & Heuristics:** Used by the security auditing modules to analyze user prompts for signs of script injection or system override attempts.

---

## 2. Code Execution Flow (Function-by-Function)

Here is exactly how prompt-craft processes prompts inside the Streamlit lifecycle:

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer (Browser)
    participant App as app.py (Streamlit)
    participant Audit as prompt_analyzer.py
    participant Client as client.py (Gemini API)

    Dev->>App: Input raw prompt & click "Optimize"
    activate App
    Note over App: Streamlit refreshes screen &<br/>stores prompt in session_state.

    App->>Audit: run_security_scan(system_instruction, template)
    activate App
    Note over Audit: Scans text for injection keyphrases<br/>(e.g., "ignore instructions", "DAN").
    Audit-->>App: returns list of security warnings & risk score
    deactivate Audit

    App->>Client: optimize_prompt_objective(objective, techniques)
    activate Client
    Note over Client: Sends instructions to Gemini to rewrite<br/>the prompt with few-shot format.
    Client-->>App: returns optimized prompt text
    deactivate Client

    App->>Client: run_completions(prompt_runs)
    activate Client
    Note over Client: Runs parallel api requests across multiple<br/>models (e.g. gemini-2.5-flash, gemini-2.0-flash).
    Client-->>App: returns token counts, latency & responses
    deactivate Client

    App-->>Dev: Displays: 1. Risk Report, 2. Optimized Prompt, 3. Cost Benchmark table
    deactivate App
```

---

## 3. Key Files and Imports Directory Map

1. **`app.py`**
   * *Entrypoint:* Renders the tabbed workspace structure (Workspace Workbench, Prompt Optimizer, Security Auditor, Model Benchmarks) and updates layout on user input.
2. **`prompt_analyzer.py`**
   * *Functions:* `scan_for_injection_attempts` and `detect_jailbreaks` scan prompt structures using regex mappings and return risk metrics.
3. **`client.py`**
   * *Functions:* Configures connection scopes and coordinates requests to model variants (like `gemini-2.5-flash`).
4. **`test_utils.py`**
   * *Class:* `AssertionEvaluator` checks LLM outputs against strict developer assertions (matching regex expressions, enforcing length limits, requiring JSON structure).
