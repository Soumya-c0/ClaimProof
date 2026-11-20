import json
from pathlib import Path
import pytest
from app.compiler.schema import CompiledPolicy
from app.engine.evaluator import evaluate_rules

CASES = [
  [
    {
      "claim_type": "flood_damage",
      "days_since_policy_start": 20,
      "claim_amount": 150000
    },
    "REJECTED"
  ],
  [
    {
      "claim_type": "flood_damage",
      "days_since_policy_start": 35,
      "claim_amount": 150000
    },
    "APPROVED"
  ],
  [
    {
      "claim_type": "flood_damage",
      "days_since_policy_start": 30,
      "claim_amount": 150000
    },
    "APPROVED"
  ],
  [
    {
      "claim_type": "flood_damage",
      "days_since_policy_start": 30,
      "claim_amount": 150001
    },
    "REJECTED"
  ]
]


@pytest.mark.parametrize('claim_input,expected', CASES)
def test_generated_policy_case(claim_input, expected):
    policy = CompiledPolicy(**json.loads(Path('compiled_policies.json').read_text(encoding='utf-8')))
    verdict, _, _ = evaluate_rules(claim_input, policy.rules)
    assert verdict == expected
