from typing import TypedDict, Literal
from app.compiler.schema import CompiledPolicy
from app.engine.schema import ClaimFacts

class ClaimState(TypedDict):
    policy: CompiledPolicy
    claim: ClaimFacts
    ambiguous_reason: str
    advocate_argument: str
    challenger_argument: str
    judge_decision: str
    confidence_score: float
    final_status: Literal["APPROVED", "REJECTED", "ESCALATED", "PENDING"]