# PromptCraft - State-of-the-Art AI Prompt Builder

PromptCraft is a premium prompt engineering studio built with a Python FastAPI backend and a Vanilla HTML/CSS/JS frontend. It integrates the official Google GenAI SDK for Gemini to design, refine, test, and audit prompts based on advanced NLP, Deep Learning, and Generative AI principles.

---

## Key Features

1. **Structured Prompt Builder**: Separates prompts into standard modular components (Persona, Core Instruction, Context, Few-Shot Demonstrations, Rule Constraints, and Formatting Style) for cleaner organization.
2. **AI Meta-Prompt Optimizer**: Connects to the Gemini API via the FastAPI server to automatically restructure and upgrade your prompt. It applies prompt engineering research (such as clear delimiters, XML bounds, and step-by-step reasoning rules) and gives a detailed breakdown of improvements.
3. **Variables Injection**: Instantly extracts placeholders like {{variable_name}} from your prompt inputs and provides dynamic text fields to test multiple scenarios in real-time.
4. **Sandbox Playground**: Test original or optimized prompts directly against Gemini models with adjustable temperature, top-p, and system instruction overrides.
5. **Quality and Security Audit**: Runs a heuristic parser to estimate token count, verify structural components, check clarity guidelines, and scan for Prompt Injection vulnerability risks on variable usage.
6. **Code Export**: Instantly exports configurations as structured JSON, clean Markdown, or production-ready integration code using the new google-genai Python SDK.

---

## NLP and Prompt Engineering Concepts Applied

* **System Instruction (Persona)**: Shapes the LLM's behavioral pattern, tone, and knowledge access.
* **Few-Shot Prompting**: Provides exemplar input-output mappings inside the prompt to reduce output variance and align formatting.
* **Chain-of-Thought**: Forces step-by-step logical reasoning before generating a response.
* **Delimitation**: Uses explicit boundaries (e.g. Markdown headers or XML tags) to partition instructions from raw input data, ensuring stability.
* **Injection Guarding**: Uses defensive constraints to protect the model from following malicious command sequences disguised as variables.

---

## Getting Started

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

### 2. Setup Environment
Navigate to the project folder and activate the virtual environment:
```bash
cd prompt_craft
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
Create a .env file in the prompt_craft directory:
```bash
cp .env.example .env
```
Populate the GEMINI_API_KEY in your .env file:
```env
GEMINI_API_KEY=your_actual_key_here
```
Note: You can also enter the API key directly in the Control Hub sidebar in the web interface.

### 5. Running the Application
Launch the FastAPI server:
```bash
python server.py
```
By default, the server will bind strictly to 127.0.0.1:8000. Open your web browser and navigate to:
http://127.0.0.1:8000

---

## Security Best Practices

* **Backend-For-Frontend (BFF) Pattern**: The frontend application does not interact directly with public APIs and does not store sensitive keys in localStorage or cookies. API keys are sent securely in POST requests to the local server, keeping keys off the client.
* **Cross-Site Scripting (XSS) Prevention**: All dynamic values and user inputs rendered within the browser are populated using safe DOM properties (textContent and innerText) or strictly HTML-escaped to prevent script execution.
* **Local Binding**: The FastAPI server runs locally and binds strictly to 127.0.0.1 (localhost) rather than 0.0.0.0, preventing external network exposure during development.
* **Prompt Injection Checks**: Built a real-time prompt injection vulnerability audit tool under the NLP Insights and Safety panel that analyzes prompt variables and alerts developers about missing delimiters or defensive instructions.
