from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.compiler.schema import CompiledPolicy
from app.engine.schema import ClaimFacts, DecisionReport
from app.engine.evaluator import execute_claim
from app.services.audit import create_audit_trail
from app.services.counterfactual import generate_counterfactuals

router = APIRouter(prefix="/claim", tags=["claim"])

class DecideRequest(BaseModel):
    policy: CompiledPolicy
    claim: ClaimFacts

@router.post("/decide", response_model=DecisionReport)
def decide_claim(request: DecideRequest):
    try:
        # 1. Execute deterministic logic
        report = execute_claim(request.policy, request.claim)
        
        # 2. Generate Hash Chain
        audit_data = create_audit_trail(request.policy, request.claim, report.status)
        report.audit = audit_data
        
        # 3. Generate Counterfactual Proofs
        counterfactuals = generate_counterfactuals(request.policy, request.claim, report)
        report.counterfactuals = counterfactuals
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")