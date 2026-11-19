import operator
from typing import Any, Dict, List, Tuple
from app.compiler.schema import PolicyRule
from app.engine.schema import RuleEvalResult, SettlementResult

OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "in": lambda a, b: a in b,
    "not_in": lambda a, b: a not in b,
}


def evaluate_rules(facts: Dict[str, Any], rules: List[PolicyRule]) -> Tuple[str, List[RuleEvalResult], bool]:
    results: List[RuleEvalResult] = []
    has_ambiguity = False
    has_failure = False

    for rule in rules:
        if rule.field not in facts or facts[rule.field] is None:
            has_ambiguity = True
            results.append(
                RuleEvalResult(
                    rule_id=rule.rule_id,
                    clause=rule.source_clause,
                    status="ambiguous",
                    reason=f"Missing fact '{rule.field}' (cl. {rule.source_clause})",
                    field=rule.field,
                    expected=rule.value,
                )
            )
            continue

        actual = facts[rule.field]
        passed = OPS[rule.operator](actual, rule.value)

        if passed:
            status = "pass"
            reason = f"{rule.description} satisfied (cl. {rule.source_clause})"
        else:
            status = "fail"
            has_failure = True
            reason = f"Got {actual}, needs {rule.operator} {rule.value} (cl. {rule.source_clause})"

        results.append(
            RuleEvalResult(
                rule_id=rule.rule_id,
                clause=rule.source_clause,
                status=status,
                reason=reason,
                field=rule.field,
                expected=rule.value,
            )
        )

    if has_ambiguity:
        verdict = "AMBIGUOUS"
    elif has_failure:
        verdict = "REJECTED"
    else:
        verdict = "APPROVED"

    return verdict, results, has_ambiguity


def calculate_settlement(
    claim_amount: float,
    verdict: str,
    deductible: float = 10000.0,
    coverage_limit: float = 500000.0,
) -> SettlementResult:
    """Deterministic payout calculator: min(claim - deductible, coverage_limit)."""
    if verdict != "APPROVED":
        payout = 0.0
    else:
        payout = max(0.0, min(claim_amount - deductible, coverage_limit))

    return SettlementResult(
        claim_amount=claim_amount,
        deductible=deductible,
        coverage_limit=coverage_limit,
        eligible_payout=payout,
    )