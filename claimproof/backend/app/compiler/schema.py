from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union

class Condition(BaseModel):
    field: str = Field(description="The claim variable to check, e.g., 'days_since_policy_start', 'loss_type'")
    operator: Literal[">", "<", ">=", "<=", "==", "!=", "in"] = Field(description="Mathematical or logical operator")
    value: Union[int, float, str, List[str]] = Field(description="The value to evaluate against")

class PolicyRule(BaseModel):
    rule_id: str = Field(description="A unique uppercase identifier, e.g., 'WAIT_30D', 'FLOOD_COVERAGE'")
    rule_type: Literal["coverage", "exclusion", "condition"] = Field(description="The nature of the rule")
    description: str = Field(description="Human readable summary of the rule")
    conditions: List[Condition] = Field(description="The logical conditions that trigger or satisfy this rule")
    coverage_limit: Optional[float] = Field(None, description="Maximum payout if applicable")
    deductible: Optional[float] = Field(None, description="Deductible to apply if applicable")
    source_clause: str = Field(description="The exact clause reference from the text, e.g., 'Clause 4.7'")

class CompiledPolicy(BaseModel):
    rules: List[PolicyRule] = Field(description="List of all extracted rules")