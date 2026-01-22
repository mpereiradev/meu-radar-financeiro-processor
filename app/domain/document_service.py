import json
import uuid
import logging
import time
from io import BytesIO
from docling.document_converter import DocumentConverter, DocumentStream
from app.config.settings import settings

logger = logging.getLogger(__name__)

"""
# DEPRECATED
"""
class DocumentService:
    def __init__(self):
        self.converter = DocumentConverter()
        self.processed_dir = settings.DATA_DIR / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def process_document(self, file_bytes: bytes, filename: str) -> dict:
        doc_uuid = str(uuid.uuid4())
        start = time.time()
        
        # Docling processing
        try:
            buf = BytesIO(file_bytes)
            source = DocumentStream(name=filename, stream=buf)
            
            # Conversion
            conv_result = self.converter.convert(source)
            conv_time = time.time() - start
            
            # Export & Save
            json_output = conv_result.document.export_to_dict()
            json_path = self.processed_dir / f"{doc_uuid}.json"
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_output, f, ensure_ascii=False, indent=2)
            
            total_time = time.time() - start
            
            # Compact log line
            logger.info(f"Processed '{filename}' ({len(file_bytes)}b) -> '{doc_uuid}.json' in {total_time:.2f}s (Conv: {conv_time:.2f}s)")
            
            return {
                "document_id": doc_uuid,
                "filename": filename,
                "json_path": str(json_path),
                "status": "processed",
                "timing": {
                    "conversion_sec": round(conv_time, 2),
                    "total_sec": round(total_time, 2)
                }
            }
        except Exception as e:
            logger.error(f"Error processing '{filename}': {e}")
            raise e
