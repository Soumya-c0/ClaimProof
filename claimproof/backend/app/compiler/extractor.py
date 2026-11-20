import json
from typing import List
import litellm
from app.compiler.schema import PolicyRule

SYSTEM_PROMPT = """
You are an insurance policy compiler. Convert tokenized policy clauses into a JSON array of rules.
Each rule MUST have these exact keys:
- rule_id (string, e.g. "FLOOD_COVERAGE", "WAIT_30D", "MAX_LIMIT")
- description (string)
- field (use ONLY: "claim_type", "days_since_policy_start", or "claim_amount")
- operator (use ONLY: "==", "!=", ">", ">=", "<", "<=", "in", "not_in")
- value (for claim_type use "flood_damage"; for numbers use integers like 30 or 150000)
- source_clause (string, e.g. "Clause 4.2")
- rule_type (use ONLY: "coverage", "waiting_period", "exclusion", "sublimit")
- linked_rules (list of strings, e.g. ["WAIT_30D"])

Keep flood coverage and waiting period as SEPARATE linked rules.
Return ONLY a raw JSON array. No markdown, no explanation.
"""

OP_FALLBACK = {
    "includes": "==",
    "contains": "==",
    "equals": "==",
    "is": "==",
    "gte": ">=",
    "lte": "<=",
    "gt": ">",
    "lt": "<",
}
VALID_TYPES = {"coverage", "waiting_period", "exclusion", "sublimit"}


def extract_rules(tokenized_policy_text: str, model: str = "groq/openai/gpt-oss-20b") -> List[PolicyRule]:
    """
    Uses LiteLLM to extract structured rules from tokenized policy text,
    then validates every rule against the PolicyRule Pydantic schema.
    """
    response = litellm.completion(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": tokenized_policy_text},
        ],
        temperature=0.0,
    )

    raw_json = response.choices[0].message.content.strip()
    if raw_json.startswith("```"):
        raw_json = raw_json.split("```")[1]
        if raw_json.startswith("json"):
            raw_json = raw_json[4:].strip()

    raw_rules = json.loads(raw_json)

    # Normalize common LLM operator/type synonyms before strict Pydantic validation
    for r in raw_rules:
        if r.get("operator") in OP_FALLBACK:
            r["operator"] = OP_FALLBACK[r["operator"]]
        if r.get("rule_type") not in VALID_TYPES:
            r["rule_type"] = "coverage"

    return [PolicyRule(**rule) for rule in raw_rules]