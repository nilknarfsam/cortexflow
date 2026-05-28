from __future__ import annotations

import json
import os
from typing import Literal

ExportFormat = Literal["txt", "md", "json"]


class ExportService:
    @staticmethod
    def format_content(text: str, fmt: ExportFormat) -> str:
        if fmt == "json":
            return json.dumps({"transcricao": text}, ensure_ascii=False, indent=2)
        if fmt == "md":
            return f"# Transcrição\n\n{text}"
        return text

    @staticmethod
    def extension_for(fmt: ExportFormat) -> str:
        return f".{fmt}"

    @staticmethod
    def build_output_path(source_path: str, output_dir: str, fmt: ExportFormat) -> str:
        base = os.path.splitext(os.path.basename(source_path))[0]
        return os.path.join(output_dir, f"{base}{ExportService.extension_for(fmt)}")

    def save(self, path: str, text: str, fmt: ExportFormat) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        content = self.format_content(text, fmt)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def save_auto(self, source_path: str, text: str, output_dir: str, fmt: ExportFormat) -> str:
        out_path = self.build_output_path(source_path, output_dir, fmt)
        return self.save(out_path, text, fmt)
