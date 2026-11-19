from typing import Any, Dict, List, Optional
from app.compiler.schema import PolicyRule
from app.engine.evaluator import evaluate_rules
from app.engine.schema import CounterfactualResult, RuleEvalResult


def run_counterfactual(
    facts: Dict[str, Any],
    rules: List[PolicyRule],
    rule_results: List[RuleEvalResult],
    original_verdict: str,
) -> Optional[CounterfactualResult]:
    failing = next((r for r in rule_results if r.status == "fail"), None)
    if not failing:
        return None

    modified_facts = dict(facts)
    original_val = facts.get(failing.field)
    modified_facts[failing.field] = failing.expected

    flipped_verdict, _, _ = evaluate_rules(modified_facts, rules)

    return CounterfactualResult(
        original_verdict=original_verdict,
        flipped_verdict=flipped_verdict,
        changed_field=failing.field,
        original_value=original_val,
        new_value=failing.expected,
        explanation=(
            f"Eligible if '{failing.field}' is {failing.expected} or greater "
            f"(was {original_val}). Re-running engine flips outcome to {flipped_verdict}."
        ),
    )