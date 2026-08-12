"""Testes do serviço de exportação nos formatos básicos."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.core.export_service import ExportService


class TestExportServiceFormatting(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ExportService()

    def test_raw_text_is_preserved(self) -> None:
        content, stage = self.service.process_content(
            "Texto sem alterações.",
            "txt",
            export_mode="raw",
        )
        self.assertEqual(content, "Texto sem alterações.")
        self.assertIsNone(stage)

    def test_raw_markdown_has_title_and_empty_placeholder(self) -> None:
        content = self.service.format_content("", "md")
        self.assertEqual(content, "# Transcrição\n\n_Sem conteúdo._\n")

    def test_raw_json_is_valid_and_preserves_accents(self) -> None:
        content = self.service.format_content("Informação útil.", "json")
        self.assertEqual(json.loads(content), {"transcricao": "Informação útil."})
        self.assertIn("Informação", content)

    def test_output_path_uses_source_stem_and_requested_extension(self) -> None:
        output = self.service.build_output_path(
            str(Path("entrada") / "aula.final.mp3"),
            str(Path("saidas")),
            "md",
        )
        self.assertEqual(Path(output), Path("saidas") / "aula.final.md")

    def test_save_auto_creates_output_and_returns_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path, stage = self.service.save_auto(
                str(Path(temp_dir) / "aula.mp3"),
                "Conteúdo exportado.",
                str(Path(temp_dir) / "resultado"),
                "txt",
            )

            self.assertIsNone(stage)
            self.assertEqual(Path(output_path).name, "aula.txt")
            self.assertEqual(
                Path(output_path).read_text(encoding="utf-8"),
                "Conteúdo exportado.",
            )


if __name__ == "__main__":
    unittest.main()
