from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.workflow import claim_workflow
from app.services.audit import get_audit_log, get_human_review_queue

router = APIRouter(prefix="/prove", tags=["Prove"])

POLICY_VERSIONS = [
    {"version": "v1", "date": "2026-01-15", "current": False},
    {"version": "v2", "date": "2026-02-20", "current": False},
    {"version": "v3", "date": "2026-03-10", "current": True},
]


class ReplayRequest(BaseModel):
    checkpoint_id: str


@router.get("/{claim_id}")
async def get_proof_bundle(claim_id: str):
    config = {"configurable": {"thread_id": claim_id}}
    history = list(claim_workflow.get_state_history(config))

    timeline = [
        {
            "checkpoint": f"CP{idx + 1}",
            "checkpoint_id": snap.config["configurable"].get("checkpoint_id"),
            "step": list(snap.next)[0] if snap.next else "Decision issued",
        }
        for idx, snap in enumerate(reversed(history))
    ]

    return {
        "claim_id": claim_id,
        "replay_timeline": timeline,
        "audit_log": get_audit_log(),
        "policy_version_history": POLICY_VERSIONS,
        "human_review_queue": get_human_review_queue(),
    }


@router.post("/{claim_id}/replay")
async def replay_from_checkpoint(claim_id: str, req: ReplayRequest):
    config = {
        "configurable": {
            "thread_id": claim_id,
            "checkpoint_id": req.checkpoint_id,
        }
    }
    replayed_state = claim_workflow.invoke(None, config=config)
    return {
        "claim_id": claim_id,
        "replayed_from": req.checkpoint_id,
        "verdict": replayed_state.get("verdict"),
        "audit_hash": replayed_state.get("audit_hash"),
    }