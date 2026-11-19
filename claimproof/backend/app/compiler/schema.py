from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field


class PolicyRule(BaseModel):
    rule_id: str
    description: str
    field: str
    operator: Literal["==", "!=", ">", ">=", "<", "<=", "in", "not_in"]
    value: Any
    source_clause: str
    rule_type: Literal["coverage", "waiting_period", "exclusion", "sublimit"]
    linked_rules: List[str] = Field(default_factory=list)


class RuleConflict(BaseModel):
    rule_a: str
    rule_b: str
    reason: str
    status: str = "needs_review"


class GeneratedTestCase(BaseModel):
    name: str
    claim_input: dict
    expected_outcome: Literal["approve", "reject", "needs_review"]
    status: Literal["pass", "fail", "needs_review"] = "pass"


class CompiledPolicy(BaseModel):
    policy_id: str = "PLC-0001"
    version: str = "v3"
    pydantic_valid: bool = True
    extracted_by: str = "LLM-extracted (LiteLLM + Ollama)"
    rules: List[PolicyRule]
    conflicts: List[RuleConflict] = Field(default_factory=list)
    generated_tests: List[GeneratedTestCase] = Field(default_factory=list)