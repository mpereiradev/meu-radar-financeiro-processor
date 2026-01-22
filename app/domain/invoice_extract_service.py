import json
import time
import uuid
import tempfile
from datetime import datetime
from pathlib import Path

import pdfplumber
from app.config.settings import settings


class InvoiceExtractService:

    def __init__(self):
        self.processed_dir = settings.DATA_DIR / "processed-invoices"
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    # =====================================================
    # PUBLIC API
    # =====================================================

    def process_pdf(self, file_bytes: bytes, filename: str) -> dict:
        """
        - Extrai texto bruto completo via pdfplumber
        - Salva JSON estruturado em disco
        - Retorna apenas metadata para API
        """

        start = time.time()
        doc_uuid = str(uuid.uuid4())

        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        ) as tmp_file:

            tmp_file.write(file_bytes)
            tmp_pdf_path = Path(tmp_file.name)

        try:
            pages_text = self._extract_text(tmp_pdf_path)

            document_payload = {
                "document_id": doc_uuid,
                "filename": filename,
                "extracted_at": datetime.utcnow().isoformat() + "Z",
                "total_pages": len(pages_text),
                "pages": pages_text
            }

            output_path = self.processed_dir / f"{doc_uuid}.json"

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    document_payload,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            total_time = time.time() - start

            return {
                "document_id": doc_uuid,
                "filename": filename,
                "status": "processed",
                "timing": {
                    "total_sec": round(total_time, 2)
                },
                "data": document_payload
            }

        finally:
            try:
                tmp_pdf_path.unlink(missing_ok=True)
            except Exception:
                pass

    # =====================================================
    # TEXTO BRUTO — PDFPLUMBER
    # =====================================================

    def _extract_text(self, pdf_path: Path) -> list[dict]:
        """
        Extração completa de texto:
        - página por página
        - linha por linha
        - sem imagens
        """

        pages = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_index, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""

                lines = [
                    line.strip()
                    for line in text.split("\n")
                    if line.strip()
                ]

                pages.append({
                    "page": page_index,
                    "content": lines
                })

        return pages
