"""Testes isolados do cache de estágios do pipeline."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.cache.cache_engine import CacheEngine


class TestCacheEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.data_dir = self.root / "data"
        self.cache_dir = self.data_dir / "cache"
        self.registry_file = self.data_dir / "cache_registry.json"
        self.source = self.root / "entrada.mp3"
        self.source.write_bytes(b"conteudo-de-audio")

        self.patches = (
            patch("src.cache.cache_engine.CACHE_DIR", self.cache_dir),
            patch("src.cache.cache_registry.DATA_DIR", self.data_dir),
            patch("src.cache.cache_registry.REGISTRY_FILE", self.registry_file),
        )
        for active_patch in self.patches:
            active_patch.start()
            self.addCleanup(active_patch.stop)

        self.engine = CacheEngine()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def lookup(self, *, mode: str = "raw", template: str = "generic", language: str = "auto"):
        return self.engine.lookup(
            str(self.source),
            export_mode=mode,
            template=template,
            language=language,
        )

    def save_stage(self, stage: str, content: str, *, mode: str = "raw") -> str:
        return self.engine.save_stage(
            str(self.source),
            stage,
            content,
            export_mode=mode,
            template="generic",
            language="auto",
        )

    def test_missing_entry_is_cache_miss(self) -> None:
        result = self.lookup()
        self.assertFalse(result.hit)
        self.assertFalse(result.partial)
        self.assertEqual(result.raw_text, "")
        self.assertTrue(result.file_hash)

    def test_raw_stage_produces_full_hit(self) -> None:
        file_hash = self.save_stage("whisper", "Transcrição em cache.")

        result = self.lookup()

        self.assertTrue(result.hit)
        self.assertTrue(result.partial)
        self.assertEqual(result.file_hash, file_hash)
        self.assertEqual(result.raw_text, "Transcrição em cache.")
        self.assertIn("whisper", result.reused_stages)

    def test_configuration_change_invalidates_lookup(self) -> None:
        self.save_stage("whisper", "Transcrição em cache.")

        changed_template = self.lookup(template="sermon")
        changed_language = self.lookup(language="pt")

        self.assertFalse(changed_template.hit)
        self.assertFalse(changed_template.partial)
        self.assertFalse(changed_language.hit)
        self.assertFalse(changed_language.partial)

    def test_clean_mode_requires_raw_and_clean_stages(self) -> None:
        self.save_stage("whisper", "Texto bruto.", mode="clean")
        partial = self.lookup(mode="clean")
        self.assertFalse(partial.hit)
        self.assertTrue(partial.partial)

        self.save_stage("clean", "# Texto limpo", mode="clean")
        complete = self.lookup(mode="clean")
        self.assertTrue(complete.hit)
        self.assertIn("clean", complete.reused_stages)

    def test_corrupted_chunks_stage_is_ignored(self) -> None:
        file_hash = self.save_stage("whisper", "Texto bruto.")
        chunks_path = self.engine._stage_path(file_hash, "chunks")
        chunks_path.write_text('{"chunks": [', encoding="utf-8")

        self.assertEqual(self.engine.read_stage(file_hash, "chunks"), "")
        result = self.lookup()
        self.assertTrue(result.hit)

    def test_corrupted_registry_starts_empty(self) -> None:
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.registry_file.write_text('{"entries": [', encoding="utf-8")

        fresh_engine = CacheEngine()

        self.assertEqual(fresh_engine.registry.entries, {})
        self.assertFalse(
            fresh_engine.lookup(
                str(self.source),
                export_mode="raw",
                template="generic",
                language="auto",
            ).hit
        )

    def test_clear_all_removes_entries_and_stage_files(self) -> None:
        file_hash = self.save_stage("whisper", "Texto bruto.")
        stage_path = self.engine._stage_path(file_hash, "whisper")
        self.assertTrue(stage_path.is_file())

        count, disk_bytes = self.engine.clear_all()

        self.assertEqual(count, 1)
        self.assertGreater(disk_bytes, 0)
        self.assertFalse(stage_path.exists())
        self.assertEqual(self.engine.registry.entries, {})
        self.assertTrue(self.cache_dir.is_dir())

    def test_chunks_stage_round_trip(self) -> None:
        content = json.dumps({"chunks": [{"id": 1, "text": "Trecho"}]})
        file_hash = self.save_stage("chunks", content)

        restored = json.loads(self.engine.read_stage(file_hash, "chunks"))

        self.assertEqual(restored["chunks"][0]["text"], "Trecho")


if __name__ == "__main__":
    unittest.main()
