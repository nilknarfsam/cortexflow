"""Testes de regressão para persistência JSON e recuperação da fila."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.cache.cache_registry import CacheRegistry
from src.core.json_storage import atomic_write_json
from src.core.persistent_queue import PersistentQueue
from src.core.settings_service import SettingsService
from src.models.transcription_job import TranscriptionJob


class _SilentLogger:
    def info(self, *_args, **_kwargs) -> None:
        pass

    def warning(self, *_args, **_kwargs) -> None:
        pass


class TestAtomicWriteJson(unittest.TestCase):
    def test_writes_valid_json_and_replaces_previous_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "state.json"
            path.write_text('{"old": true}', encoding="utf-8")

            atomic_write_json(path, {"novo": "conteúdo"})

            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"novo": "conteúdo"},
            )
            self.assertEqual(list(path.parent.glob(f".{path.name}.*.tmp")), [])

    def test_serialization_failure_preserves_previous_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "state.json"
            original = '{"preservado": true}'
            path.write_text(original, encoding="utf-8")

            with self.assertRaises(TypeError):
                atomic_write_json(path, {"invalid": {1, 2, 3}})

            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertEqual(list(path.parent.glob(f".{path.name}.*.tmp")), [])


class TestPersistentQueueRecovery(unittest.TestCase):
    def setUp(self) -> None:
        self.queue = PersistentQueue.__new__(PersistentQueue)
        self.queue._logger = _SilentLogger()

    def _restore_progress(self, value: object) -> float:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "entrada.txt"
            source.write_text("conteúdo", encoding="utf-8")
            raw = {
                "jobs": [
                    {
                        "file_path": str(source),
                        "job_progress": value,
                    }
                ]
            }
            jobs, meta = self.queue.restore_jobs(raw)
            self.assertTrue(meta["restored"])
            self.assertEqual(len(jobs), 1)
            return jobs[0].job_progress

    def test_invalid_progress_is_normalized_to_zero(self) -> None:
        self.assertEqual(self._restore_progress("inválido"), 0.0)
        self.assertEqual(self._restore_progress({"valor": 0.5}), 0.0)
        self.assertEqual(self._restore_progress("nan"), 0.0)

    def test_progress_is_limited_to_valid_range(self) -> None:
        self.assertEqual(self._restore_progress(-0.5), 0.0)
        self.assertEqual(self._restore_progress(1.5), 1.0)
        self.assertEqual(self._restore_progress("0.4"), 0.4)

    def test_dataset_metadata_survives_serialization(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "entrada.txt"
            source.write_text("conteúdo", encoding="utf-8")
            original = TranscriptionJob(
                file_path=str(source),
                dataset_metadata={"dataset_id": "ds-1", "chunks": 3},
            )

            serialized = self.queue._job_to_dict(original)
            restored = self.queue._dict_to_job(serialized)

            self.assertIsNotNone(restored)
            self.assertEqual(restored.dataset_metadata, original.dataset_metadata)

    def test_load_returns_none_for_truncated_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "queue_state.json"
            state_file.write_text('{"jobs": [', encoding="utf-8")

            with patch("src.core.persistent_queue.QUEUE_STATE_FILE", state_file):
                self.assertIsNone(self.queue.load())

    def test_restore_discards_invalid_entries_and_keeps_valid_ones(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "entrada.txt"
            source.write_text("conteúdo", encoding="utf-8")
            raw = {
                "jobs": [
                    None,
                    {"file_path": ""},
                    {
                        "file_path": str(source),
                        "status": "status-desconhecido",
                        "pipeline_progress": ["inválido"],
                    },
                ]
            }

            jobs, meta = self.queue.restore_jobs(raw)

            self.assertEqual(len(jobs), 1)
            self.assertEqual(meta["corrupted_removed"], 2)
            self.assertEqual(jobs[0].pipeline_progress, {})


class TestAtomicPersistenceIntegration(unittest.TestCase):
    def test_settings_and_history_are_written_as_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            settings_file = data_dir / "settings.json"
            history_file = data_dir / "history.json"
            service = SettingsService.__new__(SettingsService)
            service._settings = {"theme": "System"}
            service._history = [{"arquivo": "exemplo.txt"}]

            with (
                patch("src.core.settings_service.DATA_DIR", data_dir),
                patch("src.core.settings_service.SETTINGS_FILE", settings_file),
                patch("src.core.settings_service.HISTORY_FILE", history_file),
            ):
                service.save_settings()
                service.save_history()

            self.assertEqual(
                json.loads(settings_file.read_text(encoding="utf-8")),
                service._settings,
            )
            self.assertEqual(
                json.loads(history_file.read_text(encoding="utf-8")),
                service._history,
            )

    def test_cache_registry_is_written_as_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            registry_file = data_dir / "cache_registry.json"
            registry = CacheRegistry.__new__(CacheRegistry)
            registry._entries = {"hash-1": {"file_name": "entrada.txt"}}

            with (
                patch("src.cache.cache_registry.DATA_DIR", data_dir),
                patch("src.cache.cache_registry.REGISTRY_FILE", registry_file),
            ):
                registry.save()

            payload = json.loads(registry_file.read_text(encoding="utf-8"))
            self.assertEqual(payload["version"], 1)
            self.assertEqual(payload["entries"], registry._entries)


if __name__ == "__main__":
    unittest.main()
