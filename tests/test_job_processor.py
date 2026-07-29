"""Testes do pipeline de um job com dependências falsas."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.cache.cache_engine import CacheLookupResult
from src.cache.hash_manager import FileFingerprint
from src.core.job_processor import JobProcessor, QueueRunContext
from src.models.transcription_job import JobStatus, TranscriptionJob


class _FakeSettings:
    language = "auto"
    whisper_model = "base"
    export_mode = "raw"
    content_template = "generic"
    default_export_format = "txt"
    knowledge_pipeline = False
    workspace_id = "ws-default"
    collection_id = ""
    collection_name = ""

    def __init__(self, output_dir: str) -> None:
        self.output_dir = output_dir
        self.history: list[dict] = []

    def resolve_output_dir(self, _source_path: str) -> str:
        return self.output_dir

    def library_context_for_export(self, **_kwargs) -> dict:
        return {}

    def should_run_knowledge_pipeline(self, _mode: str) -> bool:
        return False

    def knowledge_pipeline_auto_enabled(self, _mode: str) -> bool:
        return False

    def add_history_entry(self, file_name: str, file_type: str, **kwargs) -> None:
        self.history.append(
            {"file_name": file_name, "file_type": file_type, **kwargs}
        )


class _FakeLibrary:
    def resolve_workspace(self, _workspace_id: str):
        return "ws-default", "Padrão"

    def resolve_collection(self, _collection_id: str, _collection_name: str):
        return "", ""


class _FakeCache:
    def __init__(self, lookup_result: CacheLookupResult | None = None) -> None:
        self.lookup_result = lookup_result or CacheLookupResult()
        self.saved_stages: list[tuple] = []
        self.saved_pipeline: list[dict] = []

    def lookup(self, *_args, **_kwargs) -> CacheLookupResult:
        return self.lookup_result

    def save_stage(self, *args, **kwargs) -> str:
        self.saved_stages.append((args, kwargs))
        return "hash-novo"

    def save_pipeline_artifacts(self, *args, **kwargs) -> None:
        self.saved_pipeline.append({"args": args, **kwargs})

    def read_stage(self, *_args, **_kwargs) -> str:
        return ""


class _FakeExtraction:
    def __init__(self, text: str = "Texto extraído.", error: Exception | None = None):
        self.text = text
        self.error = error
        self.calls = 0

    def can_extract(self, _job: TranscriptionJob) -> bool:
        return True

    def extract(self, _job: TranscriptionJob, language: str = "auto") -> str:
        self.calls += 1
        if self.error:
            raise self.error
        return self.text


class _FakeTranscription:
    is_model_loaded = False


class _FakeExport:
    def __init__(self) -> None:
        self.calls = 0

    def save_auto(self, source_path, text, output_dir, fmt, **_kwargs):
        self.calls += 1
        output = Path(output_dir) / f"{Path(source_path).stem}.{fmt}"
        output.write_text(text, encoding="utf-8")
        return str(output), None


class _FakePersistent:
    def __init__(self) -> None:
        self.checkpoints: list[str] = []

    def update_job_checkpoint(self, _job, checkpoint, **_kwargs) -> None:
        self.checkpoints.append(checkpoint)


class _SilentLogger:
    def info(self, *_args, **_kwargs) -> None:
        pass

    def warning(self, *_args, **_kwargs) -> None:
        pass

    def error(self, *_args, **_kwargs) -> None:
        pass

    def debug(self, *_args, **_kwargs) -> None:
        pass


class _ContextRecorder:
    def __init__(self, stop_values: list[bool] | None = None) -> None:
        self.stop_values = list(stop_values or [False])
        self.notifications: list[JobStatus] = []
        self.persist_calls: list[dict] = []
        self.statuses: list[str] = []
        self.completed = 0
        self.errors = 0
        self.cache_statuses: list[str] = []

    def is_stop_requested(self) -> bool:
        if len(self.stop_values) > 1:
            return self.stop_values.pop(0)
        return self.stop_values[0]

    def to_context(self) -> QueueRunContext:
        return QueueRunContext(
            is_stop_requested=self.is_stop_requested,
            on_notify=lambda job: self.notifications.append(job.status),
            on_persist=lambda **kwargs: self.persist_calls.append(kwargs),
            on_status=self.statuses.append,
            on_completed=lambda: setattr(self, "completed", self.completed + 1),
            on_error=lambda: setattr(self, "errors", self.errors + 1),
            set_last_cache_status=self.cache_statuses.append,
            recovery_meta={},
            queue_restored=False,
        )


class TestJobProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source = self.root / "entrada.txt"
        self.source.write_text("origem", encoding="utf-8")
        self.settings = _FakeSettings(str(self.root))
        self.library_patch = patch(
            "src.core.job_processor.get_library", return_value=_FakeLibrary()
        )
        self.logger_patch = patch(
            "src.core.job_processor.get_logger", return_value=_SilentLogger()
        )
        self.library_patch.start()
        self.logger_patch.start()
        self.addCleanup(self.library_patch.stop)
        self.addCleanup(self.logger_patch.stop)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def build_processor(
        self,
        *,
        cache: _FakeCache | None = None,
        extraction: _FakeExtraction | None = None,
        export: _FakeExport | None = None,
    ):
        cache = cache or _FakeCache()
        extraction = extraction or _FakeExtraction()
        export = export or _FakeExport()
        persistent = _FakePersistent()
        processor = JobProcessor(
            self.settings,
            cache=cache,
            transcription=_FakeTranscription(),
            extraction=extraction,
            export=export,
            persistent=persistent,
        )
        return processor, cache, extraction, export, persistent

    def test_fresh_document_completes_and_exports(self) -> None:
        processor, cache, extraction, export, persistent = self.build_processor()
        job = TranscriptionJob(file_path=str(self.source))
        recorder = _ContextRecorder()

        processor.process(job, recorder.to_context())

        self.assertEqual(job.status, JobStatus.COMPLETED)
        self.assertEqual(job.result_text, "Texto extraído.")
        self.assertEqual(Path(job.output_path).read_text(encoding="utf-8"), "Texto extraído.")
        self.assertEqual(recorder.completed, 1)
        self.assertEqual(recorder.errors, 0)
        self.assertEqual(extraction.calls, 1)
        self.assertEqual(export.calls, 1)
        self.assertIn("ocr", persistent.checkpoints)
        self.assertTrue(cache.saved_pipeline)
        self.assertEqual(self.settings.history[-1]["status"], "concluído")

    def test_cached_raw_text_skips_extraction(self) -> None:
        fingerprint = FileFingerprint("hash-cache", self.source.stat().st_size, self.source.name)
        cache = _FakeCache(
            CacheLookupResult(
                hit=True,
                partial=True,
                raw_text="Texto do cache.",
                reused_stages=["ocr"],
                file_hash="hash-cache",
                fingerprint=fingerprint,
            )
        )
        extraction = _FakeExtraction()
        processor, _, _, export, _ = self.build_processor(
            cache=cache, extraction=extraction
        )
        job = TranscriptionJob(file_path=str(self.source))
        recorder = _ContextRecorder()

        processor.process(job, recorder.to_context())

        self.assertEqual(job.status, JobStatus.COMPLETED)
        self.assertEqual(job.cache_status, "hit")
        self.assertEqual(job.file_hash, "hash-cache")
        self.assertEqual(extraction.calls, 0)
        self.assertEqual(export.calls, 1)

    def test_cancellation_after_extraction_is_notified_and_persisted(self) -> None:
        processor, _, _, export, _ = self.build_processor()
        job = TranscriptionJob(file_path=str(self.source))
        recorder = _ContextRecorder([False, True])

        processor.process(job, recorder.to_context())

        self.assertEqual(job.status, JobStatus.CANCELLED)
        self.assertEqual(export.calls, 0)
        self.assertEqual(recorder.notifications[-1], JobStatus.CANCELLED)
        self.assertTrue(recorder.persist_calls)

    def test_extraction_error_is_classified_and_recorded(self) -> None:
        extraction = _FakeExtraction(error=PermissionError("negado"))
        processor, _, _, export, _ = self.build_processor(extraction=extraction)
        job = TranscriptionJob(file_path=str(self.source))
        recorder = _ContextRecorder()

        processor.process(job, recorder.to_context())

        self.assertEqual(job.status, JobStatus.ERROR)
        self.assertEqual(job.error_code, "PERMISSION_DENIED")
        self.assertEqual(job.result_text, "")
        self.assertEqual(recorder.errors, 1)
        self.assertEqual(export.calls, 0)
        self.assertEqual(self.settings.history[-1]["status"], "erro")


if __name__ == "__main__":
    unittest.main()
