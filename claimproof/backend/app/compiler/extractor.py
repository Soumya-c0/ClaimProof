import json
from typing import List
import litellm
from app.compiler.schema import PolicyRule

SYSTEM_PROMPT = """
You are an insurance policy compiler. Convert tokenized policy clauses into a JSON list of rules.
Each rule must have: rule_id, description, field, operator, value, source_clause, rule_type, linked_rules.
Keep coverage clauses (e.g., flood damage) and waiting periods (e.g., 30 days) as SEPARATE linked rules.
Return ONLY valid JSON.
"""


def extract_rules(tokenized_policy_text: str, model: str = "ollama/llama3") -> List[PolicyRule]:
    response = litellm.completion(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": tokenized_policy_text},
        ],
        api_base="http://localhost:11434",
        temperature=0.0,
    )

    raw_json = response.choices[0].message.content
    raw_rules = json.loads(raw_json)

    validated_rules = [PolicyRule(**rule) for rule in raw_rules]
    return validated_rules