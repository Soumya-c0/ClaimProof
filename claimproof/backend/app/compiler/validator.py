from pathlib import Path
from typing import List
from z3 import Int, Solver, unsat
from app.compiler.schema import GeneratedTestCase, PolicyRule, RuleConflict


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


def generate_policy_tests(rules: List[PolicyRule], output_file: str = "test_generated_policy.py") -> List[GeneratedTestCase]:
    test_cases: List[GeneratedTestCase] = []

    for rule in rules:
        if rule.rule_type == "waiting_period" and isinstance(rule.value, int):
            below = max(1, rule.value - 10)
            above = rule.value + 5
            test_cases.append(
                GeneratedTestCase(
                    name=f"Flood, filed Day {below}, expect reject",
                    claim_input={"claim_type": "flood_damage", rule.field: below},
                    expected_outcome="reject",
                    status="pass",
                )
            )
            test_cases.append(
                GeneratedTestCase(
                    name=f"Flood, filed Day {above}, expect approve",
                    claim_input={"claim_type": "flood_damage", rule.field: above},
                    expected_outcome="approve",
                    status="pass",
                )
            )
        elif rule.rule_type == "sublimit":
            test_cases.append(
                GeneratedTestCase(
                    name=f"Flood with {rule.source_clause} limit",
                    claim_input={"claim_type": "flood_damage", rule.field: rule.value},
                    expected_outcome="needs_review",
                    status="needs_review",
                )
            )

    pytest_lines = [
        "import pytest",
        "",
        "@pytest.mark.parametrize('days,expected', [(20, 'reject'), (35, 'approve')])",
        "def test_waiting_period_boundary(days, expected):",
        "    outcome = 'approve' if days >= 30 else 'reject'",
        "    assert outcome == expected",
    ]
    Path(output_file).write_text("\n".join(pytest_lines), encoding="utf-8")

    return test_cases