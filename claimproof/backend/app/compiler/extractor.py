import os
from litellm import completion
from app.compiler.schema import CompiledPolicy

# Switch to the local Ollama instance
DEFAULT_MODEL = os.getenv("COMPILER_MODEL", "ollama/llama3.2")

def compile_policy_text(policy_text: str) -> CompiledPolicy:
    """Uses a local LLM to convert raw policy text into deterministic Pydantic rules."""
    
    system_prompt = """
    You are an expert insurance policy compiler. 
    Convert the following policy clauses into strict, executable structured rules in JSON format.
    Extract coverages, waiting periods, limits, and deductibles accurately.
    Use clear variable names for 'field' (e.g., 'days_since_start', 'loss_type').
    """

    response = completion(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": policy_text}
        ],
        response_format=CompiledPolicy, # Forces JSON schema adherence locally
        temperature=0.0, # Deterministic extraction
        # liteLLM automatically routes to http://localhost:11434 for ollama/ prefixes
    )
    
    # Parse the structured JSON back into our Pydantic model
    return CompiledPolicy.model_validate_json(response.choices[0].message.content)