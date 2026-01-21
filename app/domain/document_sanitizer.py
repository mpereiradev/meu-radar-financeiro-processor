import json
from pathlib import Path
from typing import Any


class DocumentSanitizer:
    """
    Responsável apenas por:
    - Ler JSON bruto do Docling
    - Remover lixo estrutural
    - Preservar textos, tabelas e grupos
    - Gerar JSON limpo para consumo por LLM
    """

    def __init__(self):
        base = Path(__file__).resolve().parents[2]
        self.input_dir = base / "data" / "processed"
        self.output_dir = base / "data" / "sanitized"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.texts = []
        self.tables = []
        self.groups = []

    # --------------------------------------------------

    def run(self):
        for file in self.input_dir.glob("*.json"):
            with open(file, encoding="utf-8") as f:
                data = json.load(f)

            self.texts = []
            self.tables = []
            self.groups = []

            self._walk(data)

            out = {
                "source_file": file.name,
                "texts": self.texts,
                "tables": self.tables,
                "groups": self.groups,
            }

            with open(self.output_dir / file.name, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=2)

            print(f"✔ sanitized {file.name}")

    # --------------------------------------------------

    def _walk(self, node: Any):
        if isinstance(node, dict):

            # ---------- TEXT ----------
            if "text" in node or "orig" in node:
                text = node.get("text") or node.get("orig")
                if isinstance(text, str) and len(text.strip()) > 0:
                    self.texts.append(
                        {
                            "text": text.strip(),
                            "label": node.get("label"),
                            "page": self._page(node),
                        }
                    )

            # ---------- TABLE ----------
            if "rows" in node and isinstance(node["rows"], list):
                rows = []
                for row in node["rows"]:
                    cells = []
                    for cell in row.get("cells", []):
                        value = cell.get("text") or cell.get("orig")
                        if value:
                            cells.append(value.strip())
                    if cells:
                        rows.append(cells)

                if rows:
                    self.tables.append(
                        {
                            "page": self._page(node),
                            "rows": rows,
                        }
                    )

            # ---------- GROUP ----------
            if node.get("label") and node.get("children"):
                self.groups.append(
                    {
                        "label": node.get("label"),
                        "children_refs": node.get("children"),
                    }
                )

            for v in node.values():
                self._walk(v)

        elif isinstance(node, list):
            for item in node:
                self._walk(item)

    # --------------------------------------------------

    def _page(self, node: dict):
        prov = node.get("prov")
        if isinstance(prov, list) and prov:
            return prov[0].get("page_no")
        return None
