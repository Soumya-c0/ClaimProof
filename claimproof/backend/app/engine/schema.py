from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel


class RuleEvalResult(BaseModel):
    rule_id: str
    clause: str
    status: Literal["pass", "fail", "ambiguous"]
    reason: str
    field: str
    expected: Any


class SettlementResult(BaseModel):
    claim_amount: float
    deductible: float
    coverage_limit: float
    eligible_payout: float


class CounterfactualResult(BaseModel):
    original_verdict: str
    flipped_verdict: str
    changed_field: str
    original_value: Any
    new_value: Any
    explanation: str