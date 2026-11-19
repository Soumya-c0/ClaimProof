import json
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel
from app.compiler.extractor import extract_rules
from app.compiler.schema import CompiledPolicy
from app.compiler.validator import detect_conflicts_z3, generate_policy_tests

router = APIRouter(prefix="/compile", tags=["Compile"])
POLICY_STORE = Path("compiled_policies.json")


class CompileRequest(BaseModel):
    policy_id: str = "PLC-0001"
    version: str = "v3"
    tokenized_text: str


@router.post("/")
async def compile_policy(req: CompileRequest) -> CompiledPolicy:
    rules = extract_rules(req.tokenized_text)
    conflicts = detect_conflicts_z3(rules)
    tests = generate_policy_tests(rules)

    compiled = CompiledPolicy(
        policy_id=req.policy_id,
        version=req.version,
        rules=rules,
        conflicts=conflicts,
        generated_tests=tests,
    )
    POLICY_STORE.write_text(compiled.model_dump_json(indent=2), encoding="utf-8")
    return compiled