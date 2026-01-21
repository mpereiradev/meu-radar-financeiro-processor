import json
import re
import unicodedata
from pathlib import Path
from collections import defaultdict
from typing import Any


class DocumentSanitizer:
    """
    Responsável por:
    - Ler JSONs processados pelo Docling
    - Identificar tipo do documento
    - Extrair apenas blocos relevantes
    - Gerar JSON sanitizado pronto para LLM
    """

    # ==============================
    # CONFIGURAÇÕES
    # ==============================

    DOCUMENT_SIGNALS = {
        "CREDIT_CARD_INVOICE": [
            "fatura",
            "cartao de credito",
            "limite disponivel",
            "pagamento minimo",
            "fechamento",
            "vencimento",
            "total da fatura",
            "parcelamento",
        ],
        "BANK_STATEMENT": [
            "extrato",
            "saldo anterior",
            "saldo atual",
            "saldo final",
            "movimentacao",
            "lancamentos",
            "debito",
            "credito",
        ],
        "PAYMENT_RECEIPT": [
            "comprovante",
            "pix realizado",
            "pagamento efetuado",
            "valor pago",
            "nsu",
            "autenticacao",
            "codigo de barras",
        ],
    }

    TRANSACTION_REGEX = {
        "date": re.compile(r"\d{2}/\d{2}/\d{4}|\d{2}/\d{2}"),
        "money": re.compile(r"r?\$?\s?\d{1,3}(\.\d{3})*,\d{2}"),
        "installment": re.compile(r"\d{1,2}/\d{1,2}"),
    }

    # ==============================
    # INIT
    # ==============================

    def __init__(self) -> None:
        # app/domain/sanitization/document_sanitizer.py
        # volta dois níveis → app/
        base_path = Path(__file__).resolve().parents[2]

        self.processed_dir = base_path / "data" / "processed"
        self.sanitized_dir = base_path / "data" / "sanitized"

        self.sanitized_dir.mkdir(parents=True, exist_ok=True)

    # ==============================
    # PUBLIC API
    # ==============================

    def run(self) -> None:
        files = list(self.processed_dir.glob("*.json"))

        if not files:
            print("Nenhum arquivo encontrado em data/processed")
            return

        for file_path in files:
            try:
                sanitized = self._process_file(file_path)

                output_path = self.sanitized_dir / file_path.name
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(sanitized, f, ensure_ascii=False, indent=2)

                print(f"✔ Sanitizado: {file_path.name}")

            except Exception as e:
                print(f"✖ Erro em {file_path.name}: {e}")

    # ==============================
    # CORE PROCESSING
    # ==============================

    def _process_file(self, file_path: Path) -> dict[str, Any]:
        with open(file_path, encoding="utf-8") as f:
            raw_json = json.load(f)

        text_blocks = self._extract_text_blocks(raw_json)
        normalized_blocks = [self._normalize_text(t) for t in text_blocks]

        document_type, confidence = self._detect_document_type(
            normalized_blocks
        )

        transaction_lines = self._extract_transaction_candidates(
            normalized_blocks
        )

        return {
            "source_file": file_path.name,
            "document_type": document_type,
            "confidence": confidence,
            "summary_blocks": normalized_blocks[:20],
            "transaction_candidates": transaction_lines,
        }

    # ==============================
    # EXTRACTION
    # ==============================

    def _extract_text_blocks(self, doc: dict) -> list[str]:
        blocks = []

        def walk(obj):
            if isinstance(obj, dict):
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for item in obj:
                    walk(item)
            elif isinstance(obj, str):
                if len(obj.strip()) > 3:
                    blocks.append(obj)

        walk(doc)
        return blocks

    # ==============================
    # NORMALIZATION
    # ==============================

    def _normalize_text(self, text: str) -> str:
        text = text.lower()
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^\w\s\/\-\.\,]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ==============================
    # DOCUMENT TYPE DETECTION
    # ==============================

    def _detect_document_type(
        self, blocks: list[str]
    ) -> tuple[str, float]:

        scores = defaultdict(int)

        for block in blocks:
            for doc_type, keywords in self.DOCUMENT_SIGNALS.items():
                for keyword in keywords:
                    if keyword in block:
                        scores[doc_type] += 1

        if not scores:
            return "UNKNOWN", 0.0

        best_type = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = round(scores[best_type] / max(total, 1), 2)

        return best_type, confidence

    # ==============================
    # TRANSACTION CANDIDATES
    # ==============================

    def _extract_transaction_candidates(
        self, blocks: list[str]
    ) -> list[str]:

        candidates = []

        for text in blocks:
            has_date = bool(self.TRANSACTION_REGEX["date"].search(text))
            has_money = bool(self.TRANSACTION_REGEX["money"].search(text))

            if has_date and has_money:
                candidates.append(text)

        return candidates[:500]  # proteção de volume
