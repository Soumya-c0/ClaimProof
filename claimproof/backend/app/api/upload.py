from fastapi import APIRouter, UploadFile, File, HTTPException
import fitz  # PyMuPDF
from app.privacy.anonymizer import protect_text

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        raw_text = ""
        
        if file.filename.endswith(".pdf"):
            # Extract text using PyMuPDF
            pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                raw_text += page.get_text("text") + "\n"
        elif file.filename.endswith(".txt"):
            # Handle plain text files for easy terminal testing
            raw_text = file_bytes.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Only PDF or TXT files are supported.")
            
        # Pass text through the Privacy Firewall
        protected_text = protect_text(raw_text)
        
        return {
            "filename": file.filename,
            "status": "processed",
            "protected_text": protected_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))