from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.compiler.schema import CompiledPolicy
from app.engine.schema import ClaimFacts, DecisionReport
from app.engine.evaluator import execute_claim
from app.services.audit import create_audit_trail
from app.services.counterfactual import generate_counterfactuals
from app.agents.workflow import claim_agent_graph # Import the graph

router = APIRouter(prefix="/claim", tags=["claim"])

class DecideRequest(BaseModel):
    policy: CompiledPolicy
    claim: ClaimFacts

@router.post("/decide", response_model=DecisionReport)
def decide_claim(request: DecideRequest):
    try:
        # 1. Execute deterministic logic
        report = execute_claim(request.policy, request.claim)
        
        # 2. Trigger LangGraph ONLY if the deterministic engine failed due to ambiguity
        if report.status == "ESCALATED":
            ambiguous_evals = [e for e in report.evaluations if e.status == "AMBIGUOUS"]
            reason = ambiguous_evals[0].reason if ambiguous_evals else "Unknown ambiguity detected."
            
            initial_state = {
                "policy": request.policy,
                "claim": request.claim,
                "ambiguous_reason": reason,
                "advocate_argument": "",
                "challenger_argument": "",
                "judge_decision": "",
                "final_status": "PENDING",
                "confidence_score": 0.0
            }
            
            # Run the agent debate
            final_state = claim_agent_graph.invoke(initial_state)
            
            # Update the report with the AI Judge's verdict
            report.status = final_state["final_status"]
            report.reason = f"Agent Review (Confidence {final_state['confidence_score']}): {final_state['judge_decision']}"
        
        # 3. Generate Hash Chain (now encompassing any agent overrides)
        audit_data = create_audit_trail(request.policy, request.claim, report.status)
        report.audit = audit_data
        
        # 4. Generate Counterfactual Proofs
        counterfactuals = generate_counterfactuals(request.policy, request.claim, report)
        report.counterfactuals = counterfactuals
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")