import hashlib
import json
from app.compiler.schema import CompiledPolicy
from app.engine.schema import ClaimFacts

def generate_hash(data: dict) -> str:
    """Generates a stable SHA-256 hash from a dictionary."""
    # Sort keys to ensure consistent hashing regardless of dictionary order
    stable_string = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(stable_string.encode('utf-8')).hexdigest()

def create_audit_trail(policy: CompiledPolicy, claim: ClaimFacts, status: str) -> dict:
    policy_hash = generate_hash(policy.model_dump())
    claim_hash = generate_hash(claim.model_dump())
    
    # The final execution hash chains the inputs and the outcome
    execution_hash = generate_hash({
        "policy_hash": policy_hash,
        "claim_hash": claim_hash,
        "status": status
    })
    
    return {
        "policy_hash": policy_hash[:8], # Truncated for frontend display
        "claim_hash": claim_hash[:8],
        "execution_hash": execution_hash[:8]
    }