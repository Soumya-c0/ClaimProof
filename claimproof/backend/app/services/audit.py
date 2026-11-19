import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

AUDIT_FILE = Path("audit_log.json")
QUEUE_FILE = Path("human_review_queue.json")


def _load_json(path: Path) -> List[Dict[str, Any]]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def _save_json(path: Path, data: List[Dict[str, Any]]) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def compute_sha256(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def record_audit_entry(
    claim_id: str,
    policy_version: str,
    claim_facts: Dict[str, Any],
    verdict: str,
    rule_ids: List[str],
    clauses: List[str],
    confidence: float,
) -> Dict[str, Any]:
    log = _load_json(AUDIT_FILE)
    prev_hash = log[-1]["hash"] if log else "GENESIS"

    fingerprint_input = {
        "prev_hash": prev_hash,
        "claim_id": claim_id,
        "policy_version": policy_version,
        "claim_facts": claim_facts,
        "verdict": verdict,
        "rule_ids": rule_ids,
        "clauses": clauses,
    }
    entry_hash = compute_sha256(fingerprint_input)

    entry = {
        "entry_id": len(log) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prev_hash": prev_hash,
        "hash": entry_hash,
        "short_hash": f"{entry_hash[:4]}...{entry_hash[-3:]}",
        "claim_id": claim_id,
        "policy_version": policy_version,
        "verdict": verdict,
        "rule_ids": rule_ids,
        "clauses": clauses,
        "confidence": confidence,
        "verified": True,
    }

    log.append(entry)
    _save_json(AUDIT_FILE, log)

    if verdict == "HUMAN_REVIEW" or confidence < 0.7:
        queue = _load_json(QUEUE_FILE)
        queue.append(
            {
                "claim_id": claim_id,
                "verdict": verdict,
                "confidence": confidence,
                "clauses": clauses,
                "status": "pending_adjuster",
            }
        )
        _save_json(QUEUE_FILE, queue)

    return entry


def get_audit_log() -> List[Dict[str, Any]]:
    return _load_json(AUDIT_FILE)


def get_human_review_queue() -> List[Dict[str, Any]]:
    return _load_json(QUEUE_FILE)