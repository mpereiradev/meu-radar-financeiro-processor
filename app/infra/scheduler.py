import json
import logging
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import List

from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

from app.infra.supabase_client import list_files, download_file, upload_file, move_file
from app.domain.invoice_extract_service import InvoiceExtractService
from app.config.settings import settings

logger = logging.getLogger(__name__)

def process_new_documents_job():
    logger.info("Starting scheduled invoice processing job.")
    
    invoice_service = InvoiceExtractService()
    invoice_prefix = "invoices"

    try:
        # 1. List files from Supabase bucket in 'invoice' folder
        # Note: We filter for files in 'invoices/' folder.
        # list_files returns paths relative to bucket root internally, e.g. "invoices/file.pdf"
        storage_files = list_files(prefix=invoice_prefix)
        
        # Filter only PDFs just in case, and ignore "invoices/" placeholder if present
        new_files = [f for f in storage_files if f.lower().endswith(".pdf") and f != "invoices/"]
        
        if not new_files:
            logger.info("No new invoice files to process.")
            return

        for filename in new_files:
            try:
                logger.info(f"Processing invoice file: {filename}")
                
                # 2. Download file
                file_bytes = download_file(invoice_prefix + "/" + filename)
                
                # 3. Process using InvoiceExtractService
                result = invoice_service.process_pdf(file_bytes, filename)
                
                # 4. Upload JSON to 'ingestion' bucket in 'invoice' folder
                # The 'data' key contains the full document payload
                if "data" in result:
                    json_data = json.dumps(result["data"], ensure_ascii=False, indent=2)
                    json_filename = f"{result['document_id']}.json"
                    upload_path = f"invoices/{json_filename}"
                    
                    # Assuming 'ingestion' bucket exists.
                    upload_file("ingestion", upload_path, json_data, "application/json")
                    logger.info(f"Uploaded extraction to ingestion/{upload_path}")
                
                # 5. Move original file to 'processed' bucket
                # filename is like "invoices/foo.pdf"
                # We want to move it to 'processed' bucket, maybe keeping structure or flat?
                # Requirement: "processed/ bucket". Let's assume flat or exact name.
                # Let's keep the filename but put it in processed bucket.
                # If we want to organize by 'invoice' in processed too: f"invoices/{Path(filename).name}"
                # The requirement says "mover ele para um outro bucket chamado processed/".
                # Let's just put it in the root of 'processed' or match the name.
                # To avoid collisions, maybe keep structure. 
                # Let's just use the full relative path in the new bucket for safety.
                
                dest_path = filename # e.g. "invoices/file.pdf"
                move_file(settings.SUPABASE_STORAGE_BUCKET, filename, "processed", dest_path)
                logger.info(f"Moved {filename} to processed/{dest_path}")
                
            except Exception as e:
                logger.error(f"Failed to process file {filename}: {e}")
                
    except Exception as e:
        logger.error(f"Job execution failed: {e}")

scheduler = BackgroundScheduler()

trigger = CronTrigger(
    hour="*", 
    minute="*", 
    timezone=ZoneInfo("America/Sao_Paulo")
)

scheduler.add_job(process_new_documents_job, trigger=trigger)

def start_scheduler():
    if not scheduler.running:
        scheduler.start()

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
