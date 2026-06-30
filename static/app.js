// Application state
const state = {
    objective: "Audit Python code for security flaws like SQL injection or path traversal, and output the issues as valid JSON.",
    persona_type: "Senior Security Auditor",
    formatting_style: "JSON",
    techniques: ["chain_of_thought", "delimitation", "injection_protection", "negative_constraints"],
    
    // Outputs from generation
    system_instruction: "",
    prompt_template: "",
    variables: {},
    current_export_type: "python"
};

// Initialize elements on DOM load
document.addEventListener("DOMContentLoaded", () => {
    initElements();
    setupEventListeners();
});

// Cache elements
let elements = {};
function initElements() {
    elements = {
        // Control Sidebar
        apiKey: document.getElementById("apiKey"),
        modelName: document.getElementById("modelName"),
        temperature: document.getElementById("temperature"),
        tempVal: document.getElementById("tempVal"),
        topP: document.getElementById("topP"),
        topPVal: document.getElementById("topPVal"),
        
        // Generator Panel Inputs
        promptObjective: document.getElementById("promptObjective"),
        personaType: document.getElementById("personaType"),
        formattingStyle: document.getElementById("formattingStyle"),
        techCoT: document.getElementById("techCoT"),
        techDelim: document.getElementById("techDelim"),
        techShield: document.getElementById("techShield"),
        techConstraints: document.getElementById("techConstraints"),
        generateBtn: document.getElementById("generateBtn"),
        
        // Workspace Placeholder and Panels
        emptyWorkspacePlaceholder: document.getElementById("emptyWorkspacePlaceholder"),
        outputWorkspace: document.getElementById("outputWorkspace"),
        sysInstruction: document.getElementById("sysInstruction"),
        promptTemplate: document.getElementById("promptTemplate"),
        variablesContainer: document.getElementById("variablesContainer"),
        
        // Navigation Tabs
        tabButtons: document.querySelectorAll(".tab-btn"),
        tabPanels: document.querySelectorAll(".tab-panel"),
        
        // Playground
        previewSystemBox: document.getElementById("previewSystemBox"),
        previewPromptBox: document.getElementById("previewPromptBox"),
        runPromptBtn: document.getElementById("runPromptBtn"),
        playgroundOutputCard: document.getElementById("playgroundOutputCard"),
        playgroundResponseBox: document.getElementById("playgroundResponseBox"),
        copyResponseBtn: document.getElementById("copyResponseBtn"),
        
        // Insights
        metricTokens: document.getElementById("metricTokens"),
        metricWords: document.getElementById("metricWords"),
        metricScore: document.getElementById("metricScore"),
        checklistContainer: document.getElementById("checklistContainer"),
        clarityContainer: document.getElementById("clarityContainer"),
        securityContainer: document.getElementById("securityContainer"),
        
        // Export
        exportTabBtns: document.querySelectorAll(".export-tab-btn"),
        exportCodeBox: document.getElementById("exportCodeBox")
    };

    // Populate initial inputs in DOM
    elements.promptObjective.value = state.objective;
    elements.personaType.value = state.persona_type;
    elements.formattingStyle.value = state.formatting_style;
}

function setupEventListeners() {
    // 1. Sidebar Sliders
    elements.temperature.addEventListener("input", (e) => {
        elements.tempVal.textContent = e.target.value;
    });
    elements.topP.addEventListener("input", (e) => {
        elements.topPVal.textContent = e.target.value;
    });

    // 2. Generate Prompt action
    elements.generateBtn.addEventListener("click", runPromptGeneration);

    // 3. Output textareas change syncer
    elements.sysInstruction.addEventListener("input", (e) => {
        state.system_instruction = e.target.value;
        triggerAnalyze();
    });

    elements.promptTemplate.addEventListener("input", (e) => {
        state.prompt_template = e.target.value;
        syncVariables();
        triggerAnalyze();
    });

    // 4. Tab Navigation
    elements.tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");
            
            // Switch active buttons
            elements.tabButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            // Switch active panels
            elements.tabPanels.forEach(panel => {
                panel.classList.remove("active");
                if (panel.id === `panel-${targetTab}`) {
                    panel.classList.add("active");
                }
            });

            // Perform transitions
            if (targetTab === "playground") {
                updatePlaygroundPreview();
            } else if (targetTab === "export") {
                updateExportCode();
            }
        });
    });

    // 5. Clipboard Copy Action Listeners
    setupClipboardButtons();

    // 6. Playground runner
    elements.runPromptBtn.addEventListener("click", executePlaygroundPrompt);

    // 7. Export Tab Buttons
    elements.exportTabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            elements.exportTabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            state.current_export_type = btn.getAttribute("data-export-type");
            updateExportCode();
        });
    });
}

// ----------------- CLIPBOARD ACTIONS -----------------

function setupClipboardButtons() {
    const copyBtns = [
        { btn: document.getElementById("copyTemplateBtn"), getVal: () => state.prompt_template },
        { btn: document.getElementById("copyResponseBtn"), getVal: () => elements.playgroundResponseBox.textContent },
        { btn: document.getElementById("copyExportBtn"), getVal: () => elements.exportCodeBox.textContent }
    ];

    copyBtns.forEach(({ btn, getVal }) => {
        if (!btn) return;
        
        btn.addEventListener("click", async () => {
            const textToCopy = getVal();
            if (!textToCopy) return;

            try {
                await navigator.clipboard.writeText(textToCopy);
                const originalText = btn.textContent;
                btn.textContent = "Copied";
                btn.style.borderColor = "var(--state-success)";
                btn.style.color = "var(--state-success)";
                
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.style.borderColor = "var(--border-color)";
                    btn.style.color = "var(--text-muted)";
                }, 2000);
            } catch (err) {
                console.error("Clipboard copy failed", err);
            }
        });
    });
}

// ----------------- DYNAMIC RENDERING & DOM BUILDERS -----------------

// Parse template string for {{variable}} patterns and render fields
function extractVariables(templateText) {
    const variables = new Set();
    const pattern = /\{\{([a-zA-Z0-9_]+)\}\}/g;
    if (templateText) {
        let match;
        // Reset state
        pattern.lastIndex = 0;
        while ((match = pattern.exec(templateText)) !== null) {
            variables.add(match[1]);
        }
    }
    return Array.from(variables).sort();
}

function syncVariables() {
    const vars = extractVariables(state.prompt_template);
    elements.variablesContainer.replaceChildren();
    
    if (vars.length === 0) {
        const p = document.createElement("p");
        p.className = "info-text";
        p.textContent = "No variable placeholders (like {{input_variable}}) detected in prompt template.";
        elements.variablesContainer.appendChild(p);
        return;
    }
    
    vars.forEach(v => {
        if (state.variables[v] === undefined) {
            state.variables[v] = "";
        }
        
        const row = document.createElement("div");
        row.className = "variable-input-row";
        
        const label = document.createElement("label");
        label.textContent = `Value for {{${v}}}`;
        label.style.display = "block";
        label.style.fontSize = "0.85rem";
        label.style.color = "var(--text-secondary)";
        label.style.marginBottom = "0.25rem";
        
        const textarea = document.createElement("textarea");
        textarea.rows = 3;
        textarea.value = state.variables[v];
        textarea.addEventListener("input", (e) => {
            state.variables[v] = e.target.value;
        });
        
        row.appendChild(label);
        row.appendChild(textarea);
        elements.variablesContainer.appendChild(row);
    });
}

function compileTemplate(template, varsMap) {
    let compiled = template;
    Object.entries(varsMap).forEach(([k, v]) => {
        compiled = compiled.replace(new RegExp(`\\{\\{${k}\\}\\}`, 'g'), v);
    });
    return compiled;
}

// ----------------- BACKEND API CALLS -----------------

async function runPromptGeneration() {
    const key = elements.apiKey.value.trim();
    const model = elements.modelName.value;
    
    // Gather techniques checklist
    const selectedTechs = [];
    if (elements.techCoT.checked) selectedTechs.push("chain_of_thought");
    if (elements.techDelim.checked) selectedTechs.push("delimitation");
    if (elements.techShield.checked) selectedTechs.push("injection_protection");
    if (elements.techConstraints.checked) selectedTechs.push("negative_constraints");
    
    state.objective = elements.promptObjective.value.trim();
    state.persona_type = elements.personaType.value.trim();
    state.formatting_style = elements.formattingStyle.value;
    state.techniques = selectedTechs;

    if (!state.objective) {
        alert("Please describe your prompt objective.");
        return;
    }

    elements.generateBtn.disabled = true;
    elements.generateBtn.textContent = "Synthesizing engineered prompt via Gemini...";

    try {
        const response = await fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                objective: state.objective,
                persona_type: state.persona_type,
                techniques: state.techniques,
                formatting_style: state.formatting_style,
                api_key: key || null,
                model_name: model
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to generate prompt structure.");
        }

        // Set state outputs
        state.system_instruction = data.generated_system_instruction || "";
        state.prompt_template = data.generated_prompt_template || "";
        state.variables = data.generated_variables || {};

        // Update DOM inputs
        elements.sysInstruction.value = state.system_instruction;
        elements.promptTemplate.value = state.prompt_template;

        // Hide placeholder and reveal Workspace
        elements.emptyWorkspacePlaceholder.classList.add("hidden");
        elements.outputWorkspace.classList.remove("hidden");

        // Sync variables fields and run quality audits
        syncVariables();
        triggerAnalyze();

    } catch (err) {
        alert("Generation Failed: " + err.message);
    } finally {
        elements.generateBtn.disabled = false;
        elements.generateBtn.textContent = "Generate Engineered Prompt";
    }
}

async function triggerAnalyze() {
    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                system_instruction: state.system_instruction,
                template: state.prompt_template
            })
        });

        if (!response.ok) return;

        const data = await response.json();
        renderAnalysisMetrics(data);
    } catch (e) {
        console.error("NLP analysis request failed", e);
    }
}

function renderAnalysisMetrics(data) {
    elements.metricTokens.textContent = data.est_tokens;
    elements.metricWords.textContent = data.word_count;
    elements.metricScore.textContent = `${data.structure_score}%`;
    
    // Checklist
    elements.checklistContainer.replaceChildren();
    Object.entries(data.checklist).forEach(([key, val]) => {
        const li = document.createElement("li");
        const dot = document.createElement("span");
        dot.className = val ? "status-indicator status-ok" : "status-indicator status-nok";
        
        const text = document.createElement("span");
        text.textContent = key;
        
        li.appendChild(dot);
        li.appendChild(text);
        elements.checklistContainer.appendChild(li);
    });

    // Clarity recommendations
    elements.clarityContainer.replaceChildren();
    data.clarity_feedback.forEach(text => {
        const li = document.createElement("li");
        li.textContent = text;
        elements.clarityContainer.appendChild(li);
    });

    // Security injection audit
    elements.securityContainer.replaceChildren();
    data.security_warnings.forEach(warn => {
        const div = document.createElement("div");
        const isSafe = warn.startsWith("Safe:");
        div.className = isSafe ? "security-item security-safe" : "security-item security-warn";
        div.textContent = warn;
        elements.securityContainer.appendChild(div);
    });
}

// ----------------- TAB PREVIEWS & TESTING -----------------

function updatePlaygroundPreview() {
    const compiled = compileTemplate(state.prompt_template, state.variables);
    elements.previewSystemBox.textContent = state.system_instruction || "(None)";
    elements.previewPromptBox.textContent = compiled || "(None)";
}

async function executePlaygroundPrompt() {
    const key = elements.apiKey.value.trim();
    const model = elements.modelName.value;
    const temp = parseFloat(elements.temperature.value);
    const pVal = parseFloat(elements.topP.value);
    
    const compiled = compileTemplate(state.prompt_template, state.variables);
    
    elements.playgroundResponseBox.textContent = "Connecting to Gemini API, please wait...";
    elements.copyResponseBtn.classList.add("hidden");
    elements.runPromptBtn.disabled = true;

    try {
        const response = await fetch("/api/test", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                assembled_prompt: compiled,
                system_instruction: state.system_instruction,
                temperature: temp,
                top_p: pVal,
                api_key: key || null,
                model_name: model
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "API execution request failed.");
        }

        elements.playgroundResponseBox.textContent = data.output;
        elements.copyResponseBtn.classList.remove("hidden");
    } catch (err) {
        elements.playgroundResponseBox.textContent = "Error: " + err.message;
    } finally {
        elements.runPromptBtn.disabled = false;
    }
}

function updateExportCode() {
    const type = state.current_export_type;
    const sys = state.system_instruction;
    const template = state.prompt_template;
    const model = elements.modelName.value;
    const temp = parseFloat(elements.temperature.value);
    const pVal = parseFloat(elements.topP.value);
    
    let content = "";
    
    if (type === "python") {
        content = `"""
Production integration using Google GenAI SDK for Gemini.
Make sure to install dependencies: pip install google-genai
"""
import os
from google import genai
from google.genai import types

def run_engineered_prompt(api_key: str = None, variables: dict = None) -> str:
    # Initialize client, resolving key from parameter or environment
    client = genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"))
    
    # 1. Base Prompt Template
    prompt_template = """${template.replace(/"""/g, '\\"\\"\\""')}"""
    
    # 2. Inject Dynamic Variables
    assembled_prompt = prompt_template
    if variables:
        for var_name, var_value in variables.items():
            assembled_prompt = assembled_prompt.replace(f"{{{{{{var_name}}}}}}", str(var_value))
            
    # 3. Model Generation Config
    config = types.GenerateContentConfig(
        system_instruction=${JSON.stringify(sys)},
        temperature=${temp},
        top_p=${pVal}
    )
    
    # 4. Generate Response
    response = client.models.generate_content(
        model="${model}",
        contents=assembled_prompt,
        config=config
    )
    return response.text

# Example execution
if __name__ == "__main__":
    test_variables = ${JSON.stringify(state.variables, null, 8)}
    # Note: TODO(security) - Never hardcode your API key. Load from environment variable.
    print(run_engineered_prompt(variables=test_variables))
`;
    } else if (type === "json") {
        const jsonExport = {
            model: model,
            temperature: temp,
            top_p: pVal,
            prompt_components: {
                system_instruction: sys,
                prompt_template: template
            }
        };
        content = JSON.stringify(jsonExport, null, 2);
    } else if (type === "markdown") {
        content = `# System Instruction / Persona\n${sys}\n\n# User Prompt Template\n${template}`;
    }
    
    elements.exportCodeBox.textContent = content;
}
