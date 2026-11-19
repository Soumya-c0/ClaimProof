import litellm
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from app.agents.state import ClaimState
from app.engine.evaluator import calculate_settlement, evaluate_rules
from app.services.counterfactual import run_counterfactual
from app.services.audit import record_audit_entry

def _ask_llm(role_prompt: str, context: str) -> str:
    resp = litellm.completion(
        model="ollama/llama3",
        api_base="http://localhost:11434",
        temperature=0.0,
        messages=[
            {"role": "system", "content": role_prompt},
            {"role": "user", "content": context},
        ],
    )
    return resp.choices[0].message.content


def evaluate_node(state: ClaimState) -> ClaimState:
    verdict, results, is_ambiguous = evaluate_rules(state["facts"], state["rules"])
    return {
        "verdict": verdict,
        "rule_results": [r.model_dump() for r in results],
        "is_ambiguous": is_ambiguous,
        "agents_triggered": False,
        "confidence": 1.0 if not is_ambiguous else 0.5,
    }


def route_after_evaluate(state: ClaimState) -> str:
    return "advocate" if state.get("is_ambiguous") else "settle"


def advocate_node(state: ClaimState) -> ClaimState:
    arg = _ask_llm(
        "You are the Advocate agent. Argue why this ambiguous insurance claim should be APPROVED.",
        str(state["rule_results"]),
    )
    args = dict(state.get("arguments", {}))
    args["advocate"] = arg
    return {"arguments": args, "agents_triggered": True}


def challenger_node(state: ClaimState) -> ClaimState:
    arg = _ask_llm(
        "You are the Challenger agent. Argue why this ambiguous insurance claim should be REJECTED.",
        str(state["rule_results"]),
    )
    args = dict(state.get("arguments", {}))
    args["challenger"] = arg
    return {"arguments": args, "agents_triggered": True}


def judge_node(state: ClaimState) -> ClaimState:
    decision = _ask_llm(
        "You are the Judge. Weigh Advocate vs Challenger against policy clauses. Reply APPROVED, REJECTED, or ESCALATE.",
        str(state.get("arguments", {})),
    )
    verdict = "APPROVED" if "APPROVED" in decision.upper() else "REJECTED"
    confidence = 0.4 if "ESCALATE" in decision.upper() else 0.85
    return {"verdict": verdict, "confidence": confidence}


def route_after_judge(state: ClaimState) -> str:
    return "human_review" if state.get("confidence", 1.0) < 0.7 else "settle"


def human_review_node(state: ClaimState) -> ClaimState:
    return {"verdict": "HUMAN_REVIEW"}


def settle_node(state: ClaimState) -> ClaimState:
    amount = float(state["facts"].get("claim_amount", 0.0))
    settlement = calculate_settlement(amount, state["verdict"])
    return {"settlement": settlement.model_dump()}


def counterfactual_node(state: ClaimState) -> ClaimState:
    from app.engine.schema import RuleEvalResult

    parsed_results = [RuleEvalResult(**r) for r in state["rule_results"]]
    cf = run_counterfactual(state["facts"], state["rules"], parsed_results, state["verdict"])
    return {"counterfactual": cf.model_dump() if cf else None}

def audit_node(state: ClaimState) -> ClaimState:
    rule_results = state.get("rule_results", [])
    rule_ids = [r["rule_id"] for r in rule_results]
    clauses = [r["clause"] for r in rule_results]

    entry = record_audit_entry(
        claim_id=state["claim_id"],
        policy_version=state.get("policy_version", "v3"),
        claim_facts=state.get("facts", {}),
        verdict=state.get("verdict", "REJECTED"),
        rule_ids=rule_ids,
        clauses=clauses,
        confidence=state.get("confidence", 1.0),
    )
    return {"audit_hash": entry["hash"]}


def build_claim_graph():
    graph = StateGraph(ClaimState)

    graph.add_node("evaluate", evaluate_node)
    graph.add_node("advocate", advocate_node)
    graph.add_node("challenger", challenger_node)
    graph.add_node("judge", judge_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("settle", settle_node)
    graph.add_node("counterfactual", counterfactual_node)

    graph.add_edge(START, "evaluate")
    graph.add_conditional_edges("evaluate", route_after_evaluate, {"advocate": "advocate", "settle": "settle"})
    graph.add_edge("advocate", "challenger")
    graph.add_edge("challenger", "judge")
    graph.add_conditional_edges("judge", route_after_judge, {"human_review": "human_review", "settle": "settle"})
    graph.add_edge("human_review", "settle")
    graph.add_edge("settle", "counterfactual")
    graph.add_node("audit", audit_node)
    graph.add_edge("counterfactual", "audit")
    graph.add_edge("audit", END)

    return graph.compile(checkpointer=MemorySaver())


claim_workflow = build_claim_graph()