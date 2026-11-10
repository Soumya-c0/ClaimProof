import os
import json
import re
from litellm import completion
from langgraph.graph import StateGraph, END
from app.agents.state import ClaimState

DEFAULT_MODEL = os.getenv("COMPILER_MODEL", "ollama/llama3.2")

def clean_json_response(raw_string: str) -> dict:
    """Helper to strip markdown formatting if the local LLM wraps the JSON."""
    match = re.search(r'\{.*\}', raw_string, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return json.loads(raw_string)

def advocate_node(state: ClaimState) -> dict:
    prompt = f"""
    Policy: {state['policy'].model_dump_json()}
    Claim: {state['claim'].model_dump_json()}
    Ambiguity: {state['ambiguous_reason']}
    
    You are the Advocate. Based strictly on the policy text, argue why this claim SHOULD be approved despite the ambiguity. Be concise.
    """
    resp = completion(model=DEFAULT_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.4)
    return {"advocate_argument": resp.choices[0].message.content}

def challenger_node(state: ClaimState) -> dict:
    prompt = f"""
    Policy: {state['policy'].model_dump_json()}
    Claim: {state['claim'].model_dump_json()}
    Ambiguity: {state['ambiguous_reason']}
    Advocate says: {state['advocate_argument']}
    
    You are the Challenger. Argue why this claim should be REJECTED based on exclusions, missing information, or invalid assumptions. Be concise.
    """
    resp = completion(model=DEFAULT_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.4)
    return {"challenger_argument": resp.choices[0].message.content}

def judge_node(state: ClaimState) -> dict:
    prompt = f"""
    Policy: {state['policy'].model_dump_json()}
    Claim: {state['claim'].model_dump_json()}
    Advocate: {state['advocate_argument']}
    Challenger: {state['challenger_argument']}
    
    You are the Judge. Evaluate the arguments against the original policy.
    Output STRICTLY in JSON format with no markdown blocks.
    Keys required: 
    "decision" (Must be exactly "APPROVED", "REJECTED", or "ESCALATED"),
    "reason" (A concise string explaining the ruling),
    "confidence" (A float between 0.0 and 1.0)
    """
    
    resp = completion(
        model=DEFAULT_MODEL, 
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    
    try:
        result = clean_json_response(resp.choices[0].message.content)
        final_decision = result.get("decision", "ESCALATED")
        confidence = float(result.get("confidence", 0.0))
        
        # If the LLM isn't confident, force human escalation
        if confidence < 0.80:
            final_decision = "ESCALATED"
            
        return {
            "judge_decision": result.get("reason", "Could not determine reason."),
            "final_status": final_decision,
            "confidence_score": confidence
        }
    except Exception as e:
        return {
            "judge_decision": f"Parsing failed: {str(e)}",
            "final_status": "ESCALATED",
            "confidence_score": 0.0
        }

# Compile the Graph
workflow = StateGraph(ClaimState)

workflow.add_node("advocate", advocate_node)
workflow.add_node("challenger", challenger_node)
workflow.add_node("judge", judge_node)

workflow.set_entry_point("advocate")
workflow.add_edge("advocate", "challenger")
workflow.add_edge("challenger", "judge")
workflow.add_edge("judge", END)

claim_agent_graph = workflow.compile()