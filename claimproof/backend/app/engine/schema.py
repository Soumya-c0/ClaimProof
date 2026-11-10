from pydantic import BaseModel, Field
from typing import Dict, Any, List, Literal
from typing import Optional
from app.compiler.schema import CompiledPolicy

class ClaimFacts(BaseModel):
    facts: Dict[str, Any] = Field(description="Key-value pairs of extracted claim variables.")
    claimed_amount: float = Field(description="The total monetary amount claimed.")

class RuleEvaluation(BaseModel):
    rule_id: str
    status: Literal["PASS", "FAIL", "AMBIGUOUS"]
    reason: str

class CounterfactualProof(BaseModel):
    failed_rule_id: str
    mutated_field: str
    original_value: Any
    required_value: Any
    would_pass: bool
    explanation: str

class AuditTrail(BaseModel):
    policy_hash: str
    claim_hash: str
    execution_hash: str

class DecisionReport(BaseModel):
    status: Literal["APPROVED", "REJECTED", "ESCALATED"]
    reason: str
    evaluations: List[RuleEvaluation]
    eligible_payout: float
    counterfactuals: List[CounterfactualProof] = []
    audit: Optional[AuditTrail] = None