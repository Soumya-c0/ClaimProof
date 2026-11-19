import json
from pathlib import Path
from typing import Any, Dict
from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.workflow import claim_workflow
from app.compiler.schema import CompiledPolicy

router = APIRouter(prefix="/decide", tags=["Decide"])
POLICY_STORE = Path("compiled_policies.json")


class DecideRequest(BaseModel):
    claim_id: str = "CLM-1042"
    facts: Dict[str, Any]


@router.post("/")
async def decide_claim(req: DecideRequest):
    compiled = CompiledPolicy(**json.loads(POLICY_STORE.read_text(encoding="utf-8")))

    initial_state = {
        "claim_id": req.claim_id,
        "facts": req.facts,
        "policy_version": compiled.version,
        "rules": compiled.rules,
    }

    config = {"configurable": {"thread_id": req.claim_id}}
    final_state = claim_workflow.invoke(initial_state, config=config)

    return {
        "claim_id": req.claim_id,
        "policy_version": compiled.version,
        "verdict": final_state["verdict"],
        "rule_trace": final_state["rule_results"],
        "settlement": final_state["settlement"],
        "counterfactual": final_state.get("counterfactual"),
        "agents_triggered": final_state.get("agents_triggered", False),
        "agent_arguments": final_state.get("arguments", {}),
    }