"""Testes do orquestrador de fila sem I/O real ou Whisper."""

from __future__ import annotations

import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from src.core.queue_manager import QueueManager
from src.models.transcription_job import JobStatus, TranscriptionJob


class _FakeSettings:
    export_mode = "raw"
    content_template = "generic"
    default_export_format = "txt"

    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir
        self.partial_history: list[dict] = []

    def resolve_output_dir(self, _source_path: str) -> str:
        return self.output_dir

    def add_partial_queue_history(self, *args, **kwargs) -> None:
        self.partial_history.append({"args": args, "kwargs": kwargs})


class _FakeTranscription:
    is_model_loaded = False

    def unload_model(self) -> None:
        raise AssertionError("Não deveria liberar modelo inexistente")


class _CompletingProcessor:
    transcription = _FakeTranscription()

    def process(self, job, ctx) -> None:
        job.status = JobStatus.COMPLETED
        job.job_progress = 1.0
        ctx.on_completed()
        ctx.on_notify(job)


class _FakeCache:
    def clear_all(self) -> tuple[int, int]:
        return (0, 0)


class _FakePersistent:
    def __init__(self) -> None:
        self.saved: list[dict] = []
        self.loaded = None
        self.restored_jobs: list[TranscriptionJob] = []
        self.restore_meta: dict = {}
        self.cleared = False

    def save(self, jobs, **kwargs) -> None:
        self.saved.append({"jobs": list(jobs), **kwargs})

    def load(self):
        return self.loaded

    def restore_jobs(self, _raw):
        return list(self.restored_jobs), dict(self.restore_meta)

    def clear_state(self) -> None:
        self.cleared = True


class _SilentLogger:
    def info(self, *_args, **_kwargs) -> None:
        pass

    def warning(self, *_args, **_kwargs) -> None:
        pass

    def error(self, *_args, **_kwargs) -> None:
        pass

    def exception(self, *_args, **_kwargs) -> None:
        pass

    def debug(self, *_args, **_kwargs) -> None:
        pass


class TestQueueManager(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.settings = _FakeSettings(str(self.root))
        self.persistent = _FakePersistent()
        self.idle = threading.Event()
        self.status_messages: list[str] = []
        self.updated: list[str] = []
        self.progress_events: list[float] = []

        self.patches = (
            patch("src.core.queue_manager.CacheEngine", return_value=_FakeCache()),
            patch("src.core.queue_manager.PersistentQueue", return_value=self.persistent),
            patch("src.core.queue_manager.get_logger", return_value=_SilentLogger()),
        )
        for active_patch in self.patches:
            active_patch.start()
            self.addCleanup(active_patch.stop)

        self.manager = QueueManager(
            self.settings,
            on_job_updated=lambda job: self.updated.append(job.id),
            on_queue_idle=self.idle.set,
            on_status_message=self.status_messages.append,
            on_progress=lambda progress, _stats: self.progress_events.append(progress),
            job_processor=_CompletingProcessor(),
        )

    def tearDown(self) -> None:
        worker = self.manager._worker
        if worker and worker.is_alive():
            worker.join(timeout=2)
        self.temp_dir.cleanup()

    def create_file(self, name: str, content: bytes = b"conteudo") -> Path:
        path = self.root / name
        path.write_bytes(content)
        return path

    def test_add_supported_file_builds_waiting_job(self) -> None:
        source = self.create_file("aula.mp3")

        added = self.manager.add_files([str(source)])

        self.assertEqual(len(added), 1)
        self.assertEqual(added[0].status, JobStatus.WAITING)
        self.assertEqual(Path(added[0].output_path), self.root / "aula.txt")
        self.assertEqual(self.manager.stats.total, 1)
        self.assertTrue(self.persistent.saved)

    def test_missing_file_is_ignored(self) -> None:
        added = self.manager.add_files([str(self.root / "ausente.mp3")])
        self.assertEqual(added, [])
        self.assertEqual(self.manager.stats.total, 0)

    def test_unsupported_file_is_visible_as_error(self) -> None:
        source = self.create_file("arquivo.xyz")

        added = self.manager.add_files([str(source)])

        self.assertEqual(added[0].status, JobStatus.ERROR)
        self.assertEqual(added[0].error_code, "INVALID_VALUE")

    def test_selected_waiting_job_can_be_removed(self) -> None:
        source = self.create_file("aula.mp3")
        job = self.manager.add_files([str(source)])[0]
        self.manager.select_job(job.id)

        self.assertTrue(self.manager.remove_selected())
        self.assertEqual(self.manager.jobs, [])
        self.assertIsNone(self.manager.selected_job)

    def test_start_queue_completes_job_and_emits_idle(self) -> None:
        source = self.create_file("aula.mp3")
        job = self.manager.add_files([str(source)])[0]

        self.assertTrue(self.manager.start_queue())
        self.assertTrue(self.idle.wait(timeout=2))
        self.manager._worker.join(timeout=2)

        self.assertEqual(job.status, JobStatus.COMPLETED)
        self.assertEqual(self.manager.stats.completed, 1)
        self.assertEqual(self.manager.get_overall_progress(), 1.0)
        self.assertIn("Fila finalizada.", self.status_messages)

    def test_start_empty_queue_is_rejected(self) -> None:
        self.assertFalse(self.manager.start_queue())
        self.assertIn("Nenhum item aguardando na fila.", self.status_messages)

    def test_recovery_tolerates_invalid_session_counters(self) -> None:
        source = self.create_file("aula.mp3")
        restored = TranscriptionJob(file_path=str(source))
        self.persistent.loaded = {
            "jobs": [{}],
            "session_completed": "inválido",
            "session_errors": -4,
        }
        self.persistent.restored_jobs = [restored]
        self.persistent.restore_meta = {"restored": True, "was_processing": False}

        self.assertTrue(self.manager.try_recover_queue())
        self.assertEqual(self.manager._session_completed, 0)
        self.assertEqual(self.manager._session_errors, 0)
        self.assertEqual(self.manager.selected_job, restored)


if __name__ == "__main__":
    unittest.main()
