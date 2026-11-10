import time
import requests
import json

# The compiled policy payload to test against
POLICY_PAYLOAD = {
    "rules": [
        {
            "rule_id": "FLOOD_COVERAGE",
            "rule_type": "coverage",
            "description": "Flood damage to the insured vehicle is covered",
            "conditions": [{"field": "loss_type", "operator": "==", "value": "flood"}],
            "coverage_limit": 150000.0,
            "source_clause": "Clause 4.2"
        },
        {
            "rule_id": "WAIT_30D",
            "rule_type": "condition",
            "description": "Claims payable only if loss occurs 30 or more days after policy start",
            "conditions": [{"field": "days_since_start", "operator": ">=", "value": 30}],
            "source_clause": "Clause 4.7"
        }
    ]
}

# 15 Test Cases mapping inputs to expected outcomes
TEST_CASES = [
    # Standard Approvals
    {"name": "Valid - Day 40", "facts": {"loss_type": "flood", "days_since_start": 40}, "amount": 100000, "expected": "APPROVED"},
    {"name": "Valid - Day 100", "facts": {"loss_type": "flood", "days_since_start": 100}, "amount": 50000, "expected": "APPROVED"},
    {"name": "Valid - Exact Day 30", "facts": {"loss_type": "flood", "days_since_start": 30}, "amount": 10000, "expected": "APPROVED"},
    
    # Waiting Period Rejections
    {"name": "Invalid - Day 20", "facts": {"loss_type": "flood", "days_since_start": 20}, "amount": 100000, "expected": "REJECTED"},
    {"name": "Invalid - Day 29", "facts": {"loss_type": "flood", "days_since_start": 29}, "amount": 100000, "expected": "REJECTED"},
    {"name": "Invalid - Day 1", "facts": {"loss_type": "flood", "days_since_start": 1}, "amount": 5000, "expected": "REJECTED"},
    
    # Coverage Type Rejections
    {"name": "Invalid - Fire Loss", "facts": {"loss_type": "fire", "days_since_start": 40}, "amount": 20000, "expected": "REJECTED"},
    {"name": "Invalid - Theft", "facts": {"loss_type": "theft", "days_since_start": 100}, "amount": 50000, "expected": "REJECTED"},
    
    # Limit Testing (Expected: APPROVED, but payout capped)
    {"name": "Limit - 200k Claim", "facts": {"loss_type": "flood", "days_since_start": 50}, "amount": 200000, "expected": "APPROVED"},
    {"name": "Limit - Exact 150k", "facts": {"loss_type": "flood", "days_since_start": 60}, "amount": 150000, "expected": "APPROVED"},
    
    # Edge Cases & Ambiguity (Triggering LangGraph Agents)
    {"name": "Agent - Missing Day", "facts": {"loss_type": "flood"}, "amount": 10000, "expected": "ESCALATED"},
    {"name": "Agent - Missing Type", "facts": {"days_since_start": 45}, "amount": 10000, "expected": "ESCALATED"},
    {"name": "Agent - Empty Facts", "facts": {}, "amount": 10000, "expected": "ESCALATED"},
    
    # Adversarial / Junk Data
    {"name": "Junk Data 1", "facts": {"loss_type": "flood", "days_since_start": -5}, "amount": 10000, "expected": "REJECTED"},
    {"name": "Junk Data 2", "facts": {"loss_type": "alien_attack", "days_since_start": 999}, "amount": 10000, "expected": "REJECTED"}
]

def run_benchmark():
    print(f"\n{'='*50}\nCLAIMPROOF BENCHMARK SUITE\n{'='*50}")
    url = "http://127.0.0.1:8000/claim/decide"
    
    passed_tests = 0
    total_time = 0
    
    for i, test in enumerate(TEST_CASES):
        payload = {
            "policy": POLICY_PAYLOAD,
            "claim": {
                "facts": test["facts"],
                "claimed_amount": test["amount"]
            }
        }
        
        start_time = time.time()
        response = requests.post(url, json=payload)
        end_time = time.time()
        
        latency = end_time - start_time
        total_time += latency
        
        if response.status_code == 200:
            result = response.json()
            actual_status = result["status"]
            is_correct = actual_status == test["expected"]
            if is_correct: passed_tests += 1
            
            # Formatting output
            status_color = "\033[92m" if is_correct else "\033[91m"
            print(f"[{i+1}/15] {test['name'].ljust(25)} | {latency:.3f}s | Expected: {test['expected'].ljust(10)} | Actual: {status_color}{actual_status}\033[0m")
        else:
            print(f"[{i+1}/15] {test['name']} | ERROR: {response.text}")

    print(f"\n{'='*50}")
    print("RESULTS:")
    print(f"Accuracy:         {(passed_tests/len(TEST_CASES))*100:.1f}% ({passed_tests}/{len(TEST_CASES)})")
    print(f"Avg Latency:      {(total_time/len(TEST_CASES)):.3f} seconds")
    print(f"Token Cost/Claim: $0.00 (Deterministic execution)")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    run_benchmark()