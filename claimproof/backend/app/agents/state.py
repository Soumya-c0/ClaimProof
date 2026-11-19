from typing import Any, Dict, List, Optional, TypedDict


class ClaimState(TypedDict, total=False):
    claim_id: str
    claim_tokens: str
    facts: Dict[str, Any]
    policy_version: str
    rules: List[Any]
    rule_results: List[Dict[str, Any]]
    conflicts: List[str]
    is_ambiguous: bool
    arguments: Dict[str, str]  # {"advocate": ..., "challenger": ...}
    verdict: str
    confidence: float
    settlement: Dict[str, Any]
    counterfactual: Optional[Dict[str, Any]]
    agents_triggered: bool
    audit_hash: str