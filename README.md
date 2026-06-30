# PromptCraft - Interactive Prompt Engineering Studio

PromptCraft is a state-of-the-art prompt engineering workspace designed to translate natural language objectives into highly optimized, production-ready LLM prompt configurations. The application utilizes a Backend-for-Frontend (BFF) architecture built with a Python FastAPI server and a Vanilla HTML5, CSS3, and JavaScript frontend. It integrates the official Google GenAI SDK for Gemini models to synthesize, evaluate, execute, and export custom prompts.

---

## Architectural Features

* **Interactive Prompt Synthesizer**: Converts raw user objectives into structured system instructions, user templates, and test variable fields.
* **Prompt Engineering Techniques**: Integrates Chain-of-Thought reasoning, XML section delimiters, prompt injection shielding, and explicit constraints.
* **Sandbox Playground**: Runs execution testing against Gemini models with adjustable temperature, top-p, and model configurations.
* **NLP and Security Auditing**: Analyzes estimated token count, structural completeness, readability, and prompt injection vulnerabilities.
* **Production Code Exporter**: Outputs copy-ready Python integration code using the new google-genai SDK, along with JSON configurations and raw Markdown templates.

---

## NLP and Prompt Engineering Concepts Applied

### 1. System Instruction (Persona Definition)
Assigns a tailored identity, domain expertise, formatting style, and behavioral constraints to the model prior to executing the user instructions.

### 2. Chain-of-Thought (Reasoning Steps)
Guides the model to generate its step-by-step thinking or logic path before outputting the final response, increasing reasoning alignment and accuracy for logical or structured tasks.

### 3. Delimitation (Boundary Partitioning)
Uses clear boundaries (such as Markdown headers or XML tags) to partition instructions, background context, and dynamic input variables, ensuring structural stability.

### 4. Injection Guarding (Security Shielding)
Instructs the model to treat dynamic variables strictly as raw untrusted data, preventing attackers from injecting malicious instructions disguised as inputs to override system rules.

---

## Technology Stack and Security Design

### Backend (Backend-for-Frontend Pattern)
The Python FastAPI server manages credentials and handles communication with the Google Gemini API. This BFF pattern keeps sensitive API keys off the client-side (no storage in localStorage or cookies) and prevents direct execution calls from client browsers.

### Frontend (Vanilla CSS & DOM Sanitization)
The user interface is built from the ground up using custom CSS (implementing dark-theme glassmorphism, responsive grids, active tab sliders, and glowing buttons) without external utility styling frameworks. All dynamically rendered content uses safe DOM properties (such as textContent and innerText) to fully protect against Cross-Site Scripting (XSS) attacks.

### Binding Strategy
To prevent unauthorized external network access during testing and development, the uvicorn process binds strictly to localhost (127.0.0.1) by default.

---

## Getting Started

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Installation
Navigate to the directory and activate the virtual environment:
```bash
cd prompt_craft
source venv/bin/activate
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. API Configuration
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Add your Gemini API Key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*Note: You can also enter the API key directly in the sidebar password field in the web interface.*

### 4. Running the App
Start the FastAPI server:
```bash
python server.py
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```
