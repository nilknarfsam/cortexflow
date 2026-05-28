from __future__ import annotations

import os
import threading
from typing import Callable, Optional

from src.core.extraction_service import ExtractionService
from src.core.export_service import ExportService
from src.core.settings_service import SettingsService
from src.core.transcription_service import TranscriptionService
from src.models.transcription_job import (
    AUDIO_EXTENSIONS,
    VIDEO_EXTENSIONS,
    JobStatus,
    TranscriptionJob,
)


JobCallback = Callable[[TranscriptionJob], None]
VoidCallback = Callable[[], None]


class QueueManager:
    def __init__(
        self,
        settings: SettingsService,
        on_job_updated: Optional[JobCallback] = None,
        on_queue_idle: Optional[VoidCallback] = None,
        on_status_message: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.settings = settings
        self._jobs: list[TranscriptionJob] = []
        self._selected_id: Optional[str] = None
        self._on_job_updated = on_job_updated
        self._on_queue_idle = on_queue_idle
        self._on_status_message = on_status_message
        self._transcription = TranscriptionService()
        self._extraction = ExtractionService()
        self._export = ExportService()
        self._worker: Optional[threading.Thread] = None
        self._stop_requested = False
        self._processing = False
        self._lock = threading.Lock()

    @property
    def jobs(self) -> list[TranscriptionJob]:
        return list(self._jobs)

    @property
    def is_processing(self) -> bool:
        return self._processing

    @property
    def selected_job(self) -> Optional[TranscriptionJob]:
        if not self._selected_id:
            return None
        return self._get_job(self._selected_id)

    def select_job(self, job_id: Optional[str]) -> None:
        self._selected_id = job_id

    def add_files(self, paths: list[str]) -> list[TranscriptionJob]:
        added: list[TranscriptionJob] = []
        for path in paths:
            path = path.strip().strip('"')
            if not path or not os.path.isfile(path):
                continue
            job = TranscriptionJob(file_path=path)
            if not job.is_supported():
                job.status = JobStatus.ERROR
                job.error_message = "Tipo de arquivo não suportado."
            output_dir = self.settings.resolve_output_dir(path)
            fmt = self.settings.default_export_format  # type: ignore[arg-type]
            job.output_path = ExportService.build_output_path(path, output_dir, fmt)
            self._jobs.append(job)
            added.append(job)
            self._notify(job)
        return added

    def remove_selected(self) -> bool:
        job = self.selected_job
        if not job or self._processing:
            return False
        if job.status == JobStatus.PROCESSING:
            return False
        self._jobs = [j for j in self._jobs if j.id != job.id]
        self._selected_id = None
        return True

    def clear_queue(self, force: bool = False) -> None:
        if self._processing and not force:
            self._jobs = [j for j in self._jobs if j.status == JobStatus.PROCESSING]
            return
        self._jobs = [j for j in self._jobs if j.status == JobStatus.PROCESSING] if self._processing else []
        if not self._processing:
            self._selected_id = None

    def start_queue(self) -> None:
        if self._processing:
            return
        pending = [j for j in self._jobs if j.status in (JobStatus.WAITING, JobStatus.ERROR)]
        if not pending:
            self._emit_status("Nenhum item aguardando na fila.")
            return
        self._stop_requested = False
        self._processing = True
        self._worker = threading.Thread(target=self._process_queue, daemon=True)
        self._worker.start()

    def stop_queue(self) -> None:
        self._stop_requested = True

    def _process_queue(self) -> None:
        try:
            for job in list(self._jobs):
                if self._stop_requested:
                    break
                if job.status not in (JobStatus.WAITING, JobStatus.ERROR):
                    continue
                self._process_job(job)
        finally:
            self._processing = False
            if self._on_queue_idle:
                self._on_queue_idle()
            self._emit_status("Fila finalizada.")

    def _process_job(self, job: TranscriptionJob) -> None:
        job.status = JobStatus.PROCESSING
        job.error_message = ""
        self._notify(job)
        self._emit_status(f"Processando: {job.file_name}")

        try:
            language = self.settings.language
            model_name = self.settings.whisper_model
            ext = job.extension

            if ext in (AUDIO_EXTENSIONS | VIDEO_EXTENSIONS):
                text = self._transcription.transcribe_media(
                    job.file_path, language=language, model_name=model_name
                )
            elif self._extraction.can_extract(job):
                text = self._extraction.extract(job, language=language)
            else:
                raise ValueError("Tipo de arquivo não suportado para transcrição.")

            job.result_text = text
            output_dir = self.settings.resolve_output_dir(job.file_path)
            fmt = self.settings.default_export_format  # type: ignore[arg-type]
            job.output_path = self._export.save_auto(job.file_path, text, output_dir, fmt)
            job.status = JobStatus.COMPLETED
            self.settings.add_history_entry(job.file_name, job.file_type)
        except Exception as exc:
            job.status = JobStatus.ERROR
            job.error_message = str(exc)
            job.result_text = ""

        self._notify(job)

    def _get_job(self, job_id: str) -> Optional[TranscriptionJob]:
        for job in self._jobs:
            if job.id == job_id:
                return job
        return None

    def _notify(self, job: TranscriptionJob) -> None:
        if self._on_job_updated:
            self._on_job_updated(job)

    def _emit_status(self, message: str) -> None:
        if self._on_status_message:
            self._on_status_message(message)
