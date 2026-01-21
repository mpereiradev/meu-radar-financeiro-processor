import json
import logging
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import List

from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

from app.infra.supabase_client import list_files, download_file
from app.domain.document_service import DocumentService
from app.config.settings import settings

logger = logging.getLogger(__name__)

# State file path using configurable DATA_DIR
STATE_FILE = settings.DATA_DIR / "state" / "processed_files.json"

def load_processed_files() -> List[str]:
    if not STATE_FILE.exists():
        return []
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading state file: {e}")
        return []

def save_processed_files(processed: List[str]):
    # Ensure directory exists
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(processed, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving state file: {e}")

def process_new_documents_job():
    logger.info("Starting scheduled document processing job.")
    
    document_service = DocumentService()
    processed_files = load_processed_files()
    
    try:
        # List all files from Supabase bucket
        storage_files = list_files()
        
        new_files = [f for f in storage_files if f not in processed_files]
        
        if not new_files:
            logger.info("No new files to process.")
            return

        for filename in new_files:
            try:
                logger.info(f"Processing file: {filename}")
                file_bytes = download_file(filename)
                
                document_service.process_document(file_bytes, filename)
                
                processed_files.append(filename)
                save_processed_files(processed_files)
                
            except Exception as e:
                logger.error(f"Failed to process file {filename}: {e}")
                
    except Exception as e:
        logger.error(f"Job execution failed: {e}")

scheduler = BackgroundScheduler()

trigger = CronTrigger(
    hour=10, 
    minute=0, 
    timezone=ZoneInfo("America/Sao_Paulo")
)

scheduler.add_job(process_new_documents_job, trigger=trigger)

def start_scheduler():
    if not scheduler.running:
        scheduler.start()

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
