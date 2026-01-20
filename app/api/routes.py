from fastapi import APIRouter, UploadFile, File, HTTPException
from app.domain.document_service import DocumentService

router = APIRouter()

# Instantiate service once or per request? 
# The service might hold state (DocumentConverter), so let's keep it global or depends.
# For simplicity and given previous context of "singleton-ish" nature of dependencies, 
# and the user requirement "No business logic in controller", I'll instantiate it here.
document_service = DocumentService()

@router.post("/documents/process")
async def process_document_endpoint(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        result = document_service.process_document(file_bytes, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
