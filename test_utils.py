import sys
import prompt_analyzer

def run_tests():
    print("Starting verification checks for prompt_analyzer.py...")

    # Test 1: Variable extraction
    fields = [
        "Translate this: {{input_text}}",
        "Context: user is name {{user_name}}"
    ]
    vars_found = prompt_analyzer.extract_variables(fields)
    assert vars_found == ["input_text", "user_name"], f"Extraction failed: {vars_found}"
    print("Passed: Test 1 - Variable extraction matches expected list.")

    # Test 2: Safe HTML escape
    malicious = "<script>alert('xss')</script>"
    escaped = prompt_analyzer.safe_html_render(malicious)
    assert escaped == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;", f"Escaping failed: {escaped}"
    print("Passed: Test 2 - HTML escaping correctly sanitizes script tags.")

    # Test 3: Template compiling
    template = "Task: Translate word {{word}} to Spanish. Input: {{word}}"
    compiled = prompt_analyzer.compile_template(template, {"word": "dog"})
    assert compiled == "Task: Translate word dog to Spanish. Input: dog", f"Compiling failed: {compiled}"
    print("Passed: Test 3 - Template compiling and variable substitution function correctly.")

    # Test 4: NLP analysis heuristics
    analysis = prompt_analyzer.analyze_prompt(
        system_instruction="Expert math solver",
        template="Solve equations: <eq>{{eq}}</eq>. Constraints: Check your work. Output JSON."
    )
    
    assert analysis["structure_score"] > 0
    assert analysis["checklist"]["Has Persona (System Instruction)"] is True
    assert analysis["checklist"]["Has Section Delimiters"] is True
    assert len(analysis["security_warnings"]) > 0
    print("Passed: Test 4 - NLP and Prompt Injection auditing outputs expected alerts.")

    print("\nAll tests completed successfully! prompt_analyzer.py functions correctly.")

if __name__ == "__main__":
    run_tests()
