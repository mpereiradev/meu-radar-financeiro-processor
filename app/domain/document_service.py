import json
import uuid
import logging
from pathlib import Path
from io import BytesIO
from docling.document_converter import DocumentConverter, DocumentStream

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        # Initialize DocumentConverter here if it's expensive, or per call.
        # Usually it's better to reuse it if it loads models.
        self.converter = DocumentConverter()
        self.processed_dir = Path("app/data/processed")
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def process_document(self, file_bytes: bytes, filename: str) -> dict:
        """
        Receives file bytes, processes with Docling, saves JSON, and returns metadata.
        """
        doc_uuid = str(uuid.uuid4())
        
        # Docling expects a file path or stream. We have bytes.
        # DocumentStream allows passing bytes directly with a name.
        buf = BytesIO(file_bytes)
        source = DocumentStream(name=filename, stream=buf)
        
        try:
            # Convert
            result = self.converter.convert(source)
            
            # Export to JSON
            # result.document is the DoclingDocument
            json_output = result.document.export_to_dict()
            
            # Save to disk
            json_path = self.processed_dir / f"{doc_uuid}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_output, f, ensure_ascii=False, indent=2)
            
            return {
                "document_id": doc_uuid,
                "filename": filename,
                "json_path": str(json_path),
                "status": "processed"
            }
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            raise e
