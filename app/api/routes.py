import logging
import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.domain.document_service import DocumentService
from app.domain.invoice_extract_service import InvoiceExtractService

logger = logging.getLogger(__name__)
router = APIRouter()
document_service = DocumentService()
invoice_extract_service = InvoiceExtractService()

"""
# DEPRECATED
"""
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

@router.post("/documents/process/invoice")
async def process_document_invoice_endpoint(file: UploadFile = File(...)):
    start = time.time()
    try:
        content = await file.read()
        result = invoice_extract_service.process_pdf(content, file.filename)
        logger.info(f"API /documents/process/invoice: '{file.filename}' processed in {time.time() - start:.2f}s")
        return result
    except Exception as e:
        logger.error(f"API Error processing '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail=str(e))