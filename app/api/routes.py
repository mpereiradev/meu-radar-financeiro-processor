import logging
import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.domain.document_service import DocumentService
from app.domain.document_sanitizer import DocumentSanitizer

logger = logging.getLogger(__name__)
router = APIRouter()
document_service = DocumentService()
document_sanitizer = DocumentSanitizer()

@router.post("/documents/process")
async def process_document_endpoint(file: UploadFile = File(...)):
    start = time.time()
    try:
        content = await file.read()
        result = document_service.process_document(content, file.filename)
        logger.info(f"API /documents/process: '{file.filename}' processed in {time.time() - start:.2f}s")
        return result
    except Exception as e:
        logger.error(f"API Error processing '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/sanitize")
async def sanitize_document_endpoint():
    start = time.time()
    try:
        document_sanitizer.run()
        logger.info(f"API /documents/sanitize: sanitized in {time.time() - start:.2f}s")
        return {"status": "sanitized"}
    except Exception as e:
        logger.error(f"API Error sanitizing: {e}")
        raise HTTPException(status_code=500, detail=str(e))
