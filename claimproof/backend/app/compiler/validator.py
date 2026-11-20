import json
from pathlib import Path
from typing import Any, Dict, List
from z3 import Int, Solver, unsat
from app.compiler.schema import GeneratedTestCase, PolicyRule, RuleConflict
from app.engine.evaluator import evaluate_rules

VERDICT_OF = {"approve": "APPROVED", "reject": "REJECTED", "needs_review": "AMBIGUOUS"}


def detect_conflicts_z3(rules: List[PolicyRule]) -> List[RuleConflict]:
    conflicts: List[RuleConflict] = []
    limit_rules = [r for r in rules if r.field == "claim_amount" and isinstance(r.value, (int, float))]

    for i in range(len(limit_rules)):
        for j in range(i + 1, len(limit_rules)):
            r1, r2 = limit_rules[i], limit_rules[j]
            s = Solver()
            amount = Int("claim_amount")
            s.add(amount <= int(r1.value))
            s.add(amount > int(r2.value))

            if s.check() != unsat:
                conflicts.append(
                    RuleConflict(
                        rule_a=r1.source_clause,
                        rule_b=r2.source_clause,
                        reason=f"Clause {r1.source_clause} vs {r2.source_clause}: overlapping limits ({r1.value} vs {r2.value})",
                    )
                )

    return conflicts


def _passing_value(rule: PolicyRule) -> Any:
    """A fact value that satisfies the rule, used to build a claim that only fails the rule under test."""
    op, v = rule.operator, rule.value
    if op == "in":
        return v[0] if isinstance(v, list) and v else v
    if op == ">":
        return v + 1
    if op == "<":
        return v - 1
    if op == "!=":
        return f"not_{v}"
    if op == "not_in":
        return "__other__"
    return v  # ==, >=, <=


def generate_policy_tests(rules: List[PolicyRule], output_file: str = "test_generated_policy.py") -> List[GeneratedTestCase]:
    """Builds boundary tests from the rules, RUNS them through the rule engine, and writes a real pytest file."""
    base: Dict[str, Any] = {r.field: _passing_value(r) for r in rules}
    specs = []  # (name, claim_input, expected_outcome)

    for rule in rules:
        if rule.rule_type == "waiting_period" and isinstance(rule.value, int) and rule.operator == ">=":
            below, above = max(1, rule.value - 10), rule.value + 5
            specs.append((f"Flood, filed Day {below}, expect reject", {**base, rule.field: below}, "reject"))
            specs.append((f"Flood, filed Day {above}, expect approve", {**base, rule.field: above}, "approve"))
        elif rule.rule_type == "sublimit" and isinstance(rule.value, (int, float)) and rule.operator == "<=":
            specs.append((f"Claim at {rule.source_clause} limit, expect approve", {**base, rule.field: rule.value}, "approve"))
            specs.append((f"Claim above {rule.source_clause} limit, expect reject", {**base, rule.field: rule.value + 1}, "reject"))

    test_cases: List[GeneratedTestCase] = []
    for name, claim_input, expected in specs:
        verdict, _, _ = evaluate_rules(claim_input, rules)
        test_cases.append(
            GeneratedTestCase(
                name=name,
                claim_input=claim_input,
                expected_outcome=expected,
                status="pass" if verdict == VERDICT_OF[expected] else "fail",
            )
        )

    cases = [[c.claim_input, VERDICT_OF[c.expected_outcome]] for c in test_cases]
    pytest_lines = [
        "import json",
        "from pathlib import Path",
        "import pytest",
        "from app.compiler.schema import CompiledPolicy",
        "from app.engine.evaluator import evaluate_rules",
        "",
        f"CASES = {json.dumps(cases, indent=2)}",
        "",
        "",
        "@pytest.mark.parametrize('claim_input,expected', CASES)",
        "def test_generated_policy_case(claim_input, expected):",
        "    policy = CompiledPolicy(**json.loads(Path('compiled_policies.json').read_text(encoding='utf-8')))",
        "    verdict, _, _ = evaluate_rules(claim_input, policy.rules)",
        "    assert verdict == expected",
    ]
    Path(output_file).write_text("\n".join(pytest_lines) + "\n", encoding="utf-8")

    return test_cases
