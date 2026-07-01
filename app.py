import streamlit as st
import config
import client
import prompt_analyzer

# Page configuration
st.set_page_config(
    page_title="PromptCraft - Interactive Prompt Engineering Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (Dark Mode theme overrides)
st.markdown("""
<style>
    /* Dark Theme Cohesive Palette */
    :root {
        --bg-primary: #0d1117;
        --bg-secondary: #161b22;
        --border-color: #30363d;
        --accent-color: #58a6ff;
        --text-color: #c9d1d9;
    }
    
    /* Global styles */
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-color);
    }
    
    /* Code and metrics containers styling */
    div[data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif;
        color: var(--accent-color) !important;
        font-size: 2.2rem !important;
    }
    
    /* Security and clarity boxes */
    .security-safe {
        background-color: rgba(46, 160, 67, 0.1);
        border: 1px solid rgba(46, 160, 67, 0.4);
        border-radius: 6px;
        padding: 10px 15px;
        margin-bottom: 10px;
        color: #58a6ff;
    }
    
    .security-warn {
        background-color: rgba(248, 81, 73, 0.1);
        border: 1px solid rgba(248, 81, 73, 0.4);
        border-radius: 6px;
        padding: 10px 15px;
        margin-bottom: 10px;
        color: #f85149;
    }
    
    .clarity-item {
        background-color: rgba(240, 139, 55, 0.05);
        border-left: 3px solid rgba(240, 139, 55, 0.4);
        padding: 8px 12px;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# State initialization
if "system_instruction" not in st.session_state:
    st.session_state.system_instruction = ""
if "prompt_template" not in st.session_state:
    st.session_state.prompt_template = ""
if "variables" not in st.session_state:
    st.session_state.variables = {}
if "playground_output" not in st.session_state:
    st.session_state.playground_output = ""

# Sidebar settings
st.sidebar.title("Parameters")

_env_api_key = config.get_api_key()

api_key_input = st.sidebar.text_input(
    "Gemini API Key",
    type="password",
    value="",
    placeholder="Using GEMINI_API_KEY from environment" if _env_api_key else "Enter your Gemini API Key",
    help="Enter your Gemini API Key or set it as GEMINI_API_KEY environment variable."
)

# Resolve API Key (never pre-fill the visible field with the real secret,
# since Streamlit renders the input's value into the page even when masked)
resolved_api_key = api_key_input.strip() if api_key_input.strip() else _env_api_key

model_name = st.sidebar.selectbox(
    "Model Selection",
    options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
    index=0
)

temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=2.0,
    value=config.DEFAULT_TEMP,
    step=0.05
)

top_p = st.sidebar.slider(
    "Top P",
    min_value=0.0,
    max_value=1.0,
    value=config.DEFAULT_TOP_P,
    step=0.05
)

# Main Title Header
st.title("PromptCraft")
st.caption("State-of-the-art prompt synthesis, sandbox playground, and NLP safety auditing workspace.")

# Left / Right side layout columns
col_inputs, col_workspace = st.columns([1, 1.3])

with col_inputs:
    st.header("1. Input Objective")
    
    objective = st.text_area(
        "Prompt Objective",
        value="Audit Python code for security flaws like SQL injection or path traversal, and output the issues as valid JSON.",
        height=100
    )
    
    persona_type = st.text_input(
        "Persona / Role",
        value="Senior Security Auditor"
    )
    
    st.write("Techniques")
    tech_cot = st.checkbox("Chain-of-Thought reasoning", value=True)
    tech_delim = st.checkbox("Boundary XML delimiters", value=True)
    tech_shield = st.checkbox("Prompt Injection Protection", value=True)
    tech_constraints = st.checkbox("Negative Constraints", value=True)
    
    formatting_style = st.selectbox(
        "Formatting Style",
        options=["JSON", "Markdown", "Plain Text"],
        index=0
    )
    
    generate_btn = st.button("Generate Engineered Prompt", use_container_width=True)
    
    if generate_btn:
        if not objective.strip():
            st.error("Please describe your prompt objective.")
        elif not resolved_api_key:
            st.error("Gemini API Key is missing. Enter it in the sidebar to generate prompt layouts.")
        else:
            selected_techniques = []
            if tech_cot: selected_techniques.append("chain_of_thought")
            if tech_delim: selected_techniques.append("delimitation")
            if tech_shield: selected_techniques.append("injection_protection")
            if tech_constraints: selected_techniques.append("negative_constraints")
            
            with st.spinner("Synthesizing prompt template via Gemini..."):
                try:
                    generated_data = client.generate_prompt_structure_with_gemini(
                        api_key=resolved_api_key,
                        model_name=model_name,
                        objective=objective,
                        persona_type=persona_type,
                        techniques=selected_techniques,
                        formatting_style=formatting_style
                    )
                    
                    st.session_state.system_instruction = generated_data.get("generated_system_instruction", "")
                    st.session_state.prompt_template = generated_data.get("generated_prompt_template", "")
                    st.session_state.variables = generated_data.get("generated_variables", {})
                    st.success("Generation completed.")
                except Exception as e:
                    st.error(f"Generation failed: {str(e)}")

with col_workspace:
    st.header("2. Workspace Output")
    
    if not st.session_state.system_instruction and not st.session_state.prompt_template:
        st.info("Input prompt parameters and click 'Generate Engineered Prompt' to populate prompt structures.")
    else:
        # Render dynamic workspace tabs
        tab_editor, tab_sandbox, tab_diagnostics, tab_export = st.tabs([
            "Prompt Editor",
            "Playground Sandbox",
            "Safety & Analytics",
            "Export Code"
        ])
        
        with tab_editor:
            # Main editor text fields (updates state on input)
            sys_edit = st.text_area(
                "System Instruction",
                value=st.session_state.system_instruction,
                height=150
            )
            st.session_state.system_instruction = sys_edit
            
            template_edit = st.text_area(
                "User Prompt Template",
                value=st.session_state.prompt_template,
                height=250
            )
            st.session_state.prompt_template = template_edit
            
            # Local variable syncing
            variables_detected = prompt_analyzer.extract_variables([st.session_state.prompt_template])
            
            if variables_detected:
                st.write("Dynamic Test Variables")
                updated_vars = {}
                for v in variables_detected:
                    default_v = st.session_state.variables.get(v, "")
                    val = st.text_area(f"Value for {{{{ {v} }}}}", value=default_v, height=70)
                    updated_vars[v] = val
                st.session_state.variables = updated_vars
            else:
                st.caption("No variable placeholders detected (like {{variable_name}}).")
        
        with tab_sandbox:
            # Compiled preview
            compiled_prompt = prompt_analyzer.compile_template(
                st.session_state.prompt_template,
                st.session_state.variables
            )
            
            st.subheader("Sandbox Previews")
            st.text_area("Assembled System Instruction", value=st.session_state.system_instruction, height=80, disabled=True)
            st.text_area("Assembled Compiled Prompt", value=compiled_prompt, height=200, disabled=True)
            
            run_btn = st.button("Run Sandbox Test", use_container_width=True)
            
            if run_btn:
                if not resolved_api_key:
                    st.error("Please enter a valid Gemini API Key to run sandbox tests.")
                else:
                    with st.spinner("Executing prompt sandbox test..."):
                        res = client.test_prompt(
                            api_key=resolved_api_key,
                            model_name=model_name,
                            assembled_prompt=compiled_prompt,
                            system_instruction=st.session_state.system_instruction,
                            temperature=temperature,
                            top_p=top_p
                        )
                        st.session_state.playground_output = res
            
            if st.session_state.playground_output:
                st.subheader("Model Output")
                st.code(st.session_state.playground_output, language="text")
        
        with tab_diagnostics:
            # Run local checks
            analysis = prompt_analyzer.analyze_prompt(
                st.session_state.system_instruction,
                st.session_state.prompt_template
            )
            
            # Metrics
            met_col1, met_col2, met_col3 = st.columns(3)
            met_col1.metric("Est. Tokens", analysis["est_tokens"])
            met_col2.metric("Word Count", analysis["word_count"])
            met_col3.metric("Structure Score", f"{analysis['structure_score']}%")
            
            # Checklist
            st.subheader("Quality Checklist")
            for k, val in analysis["checklist"].items():
                status_color = "green" if val else "red"
                st.markdown(f"<span style='color:{status_color}; font-size:1.2rem; margin-right:8px;'>●</span> {k}", unsafe_allow_html=True)
                
            # Clarity recommendations
            st.subheader("Clarity Diagnostics")
            for text in analysis["clarity_feedback"]:
                st.markdown(f"<div class='clarity-item'>{text}</div>", unsafe_allow_html=True)
                
            # Security Threat Auditing
            st.subheader("Prompt Injection Audit")
            for warn in analysis["security_warnings"]:
                if warn.startswith("Safe:"):
                    st.markdown(f"<div class='security-safe'>{warn}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='security-warn'>{warn}</div>", unsafe_allow_html=True)
                    
        with tab_export:
            # Integration Code blocks
            export_format = st.selectbox(
                "Export Format",
                options=["Python GenAI SDK", "JSON Structure", "Raw Markdown"],
                index=0
            )
            
            if export_format == "Python GenAI SDK":
                python_code = f'''"""
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
    prompt_template = """{st.session_state.prompt_template}"""
    
    # 2. Inject Dynamic Variables
    assembled_prompt = prompt_template
    if variables:
        for var_name, var_value in variables.items():
            assembled_prompt = assembled_prompt.replace(f"{{{{{{var_name}}}}}}", str(var_value))
            
    # 3. Model Generation Config
    config = types.GenerateContentConfig(
        system_instruction={repr(st.session_state.system_instruction)},
        temperature={temperature},
        top_p={top_p}
    )
    
    # 4. Generate Response
    response = client.models.generate_content(
        model="{model_name}",
        contents=assembled_prompt,
        config=config
    )
    return response.text

# Example execution
if __name__ == "__main__":
    test_variables = {repr(st.session_state.variables)}
    # Note: TODO(security) - Never hardcode your API key. Load from environment variable.
    print(run_engineered_prompt(variables=test_variables))
'''
                st.code(python_code, language="python")
                
            elif export_format == "JSON Structure":
                import json
                json_export = {
                    "model": model_name,
                    "temperature": temperature,
                    "top_p": top_p,
                    "prompt_components": {
                        "system_instruction": st.session_state.system_instruction,
                        "prompt_template": st.session_state.prompt_template
                    }
                }
                st.code(json.dumps(json_export, indent=2), language="json")
                
            elif export_format == "Raw Markdown":
                markdown_export = f"# System Instruction / Persona\n\n{st.session_state.system_instruction}\n\n# User Prompt Template\n\n{st.session_state.prompt_template}"
                st.code(markdown_export, language="markdown")
