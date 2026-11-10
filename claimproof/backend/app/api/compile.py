from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.compiler.extractor import compile_policy_text
from app.compiler.schema import CompiledPolicy

router = APIRouter(prefix="/policy", tags=["policy"])

class CompileRequest(BaseModel):
    policy_text: str

@router.post("/compile", response_model=CompiledPolicy)
def compile_policy(request: CompileRequest):
    try:
        compiled_rules = compile_policy_text(request.policy_text)
        return compiled_rules
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compilation failed: {str(e)}")