import uuid
import fitz  
from fastapi import APIRouter, File, Form, UploadFile
from typing import Optional
from app.privacy.anonymizer import anonymize_text
from app.privacy.vault import vault

router = APIRouter(prefix="/protect", tags=["Protect"])


def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def extract_text_from_image(file_bytes: bytes) -> str:
    from paddleocr import PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang="en")
    result = ocr.ocr(file_bytes, cls=True)
    lines = [line[1][0] for block in (result or []) for line in (block or [])]
    return "\n".join(lines)


@router.post("/upload")
async def protect_document(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    doc_type: str = Form("claim"), 
):
    doc_id = str(uuid.uuid4())[:8]
    extracted_text = raw_text or ""

    if file:
        content = await file.read()
        filename = (file.filename or "").lower()
        if filename.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(content)
        elif filename.endswith((".png", ".jpg", ".jpeg")):
            extracted_text = extract_text_from_image(content)
        else:
            extracted_text = content.decode("utf-8", errors="ignore")

    tokenized_text, token_map, privacy_check = anonymize_text(extracted_text, doc_type)

    vault.save_map(doc_id, token_map)

    return {
        "doc_id": doc_id,
        "doc_type": doc_type,
        "filename": file.filename if file else "raw_text.txt",
        "status": "parsed",
        "tokenized_text": tokenized_text,
        "privacy_check": privacy_check,
        "notice": "Only tokenised text reaches the LLM. Token map is stored locally.",
    }