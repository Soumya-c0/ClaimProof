from app.compiler.schema import CompiledPolicy, Condition
from app.engine.schema import ClaimFacts, RuleEvaluation, DecisionReport

def evaluate_condition(condition: Condition, facts: dict) -> bool:
    """Safely executes the mathematical operator against the claim facts."""
    if condition.field not in facts:
        raise ValueError(f"Missing required claim fact: {condition.field}")

    fact_val = facts[condition.field]
    cond_val = condition.value

    # Deterministic evaluation matrix
    if condition.operator == "==": return fact_val == cond_val
    if condition.operator == "!=": return fact_val != cond_val
    if condition.operator == ">": return fact_val > cond_val
    if condition.operator == ">=": return fact_val >= cond_val
    if condition.operator == "<": return fact_val < cond_val
    if condition.operator == "<=": return fact_val <= cond_val
    if condition.operator == "in": return fact_val in cond_val

    raise ValueError(f"Unknown operator: {condition.operator}")

def execute_claim(policy: CompiledPolicy, claim: ClaimFacts) -> DecisionReport:
    evaluations = []
    final_status = "APPROVED"
    rejection_reason = "All policy conditions met."
    payout = claim.claimed_amount

    for rule in policy.rules:
        rule_status = "PASS"
        failure_reason = ""

        # 1. Evaluate all conditions tied to this rule
        for cond in rule.conditions:
            try:
                passed = evaluate_condition(cond, claim.facts)
                if not passed:
                    rule_status = "FAIL"
                    failure_reason = f"Actual '{cond.field}' ({claim.facts.get(cond.field)}) failed requirement: {cond.operator} {cond.value}"
                    break
            except ValueError as e:
                rule_status = "AMBIGUOUS"
                failure_reason = str(e)
                break

        # 2. Record the trace
        evaluations.append(RuleEvaluation(
            rule_id=rule.rule_id,
            status=rule_status,
            reason=failure_reason if rule_status != "PASS" else rule.description
        ))

        # 3. Apply Decision Logic
        if rule_status == "AMBIGUOUS":
            final_status = "ESCALATED"
            rejection_reason = f"Agent verification required due to missing fact: {failure_reason}"
            payout = 0.0
            break 
            
        if rule_status == "FAIL":
            final_status = "REJECTED"
            rejection_reason = f"Policy requirement not met: {failure_reason}"
            payout = 0.0

        # 4. Apply Financial Mathematics (only if no failure yet)
        if final_status == "APPROVED" and rule_status == "PASS":
            if rule.deductible:
                payout = max(0.0, payout - rule.deductible)
            if rule.coverage_limit:
                payout = min(payout, rule.coverage_limit)

    return DecisionReport(
        status=final_status,
        reason=rejection_reason,
        evaluations=evaluations,
        eligible_payout=payout if final_status == "APPROVED" else 0.0
    )