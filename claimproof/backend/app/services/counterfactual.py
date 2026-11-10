import copy
from app.compiler.schema import CompiledPolicy
from app.engine.schema import ClaimFacts, CounterfactualProof
from app.engine.evaluator import execute_claim

def generate_counterfactuals(policy: CompiledPolicy, original_claim: ClaimFacts, original_report) -> list[CounterfactualProof]:
    proofs = []
    
    # Only generate counterfactuals for rejected claims
    if original_report.status != "REJECTED":
        return proofs

    # Find which rules failed
    failed_evaluations = [e for e in original_report.evaluations if e.status == "FAIL"]
    
    for failed_eval in failed_evaluations:
        # Find the actual rule definition
        rule = next((r for r in policy.rules if r.rule_id == failed_eval.rule_id), None)
        if not rule:
            continue
            
        for condition in rule.conditions:
            if condition.field in original_claim.facts:
                original_val = original_claim.facts[condition.field]
                target_val = condition.value
                
                # Clone the claim and mutate the specific failing fact to the boundary requirement
                mutated_claim = copy.deepcopy(original_claim)
                mutated_claim.facts[condition.field] = target_val
                
                # Re-run the deterministic engine with the mutated fact
                test_report = execute_claim(policy, mutated_claim)
                
                # Check if this specific rule now passes
                rule_now_passes = any(e.status == "PASS" for e in test_report.evaluations if e.rule_id == rule.rule_id)
                
                if rule_now_passes:
                    proofs.append(CounterfactualProof(
                        failed_rule_id=rule.rule_id,
                        mutated_field=condition.field,
                        original_value=original_val,
                        required_value=target_val,
                        would_pass=True,
                        explanation=f"If the {condition.field} was {target_val} instead of {original_val}, rule {rule.rule_id} would pass."
                    ))
                    
    return proofs