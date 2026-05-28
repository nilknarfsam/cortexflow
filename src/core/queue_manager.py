from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from typing import Callable, Optional

from src.core.extraction_service import ExtractionService
from src.core.export_service import ExportService
from src.core.job_errors import classify_job_error, format_traceback
from src.core.log_service import get_logger
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
ProgressCallback = Callable[[float, "QueueStats"], None]


@dataclass(frozen=True)
class QueueStats:
    total: int
    waiting: int
    processing: int
    completed: int
    errors: int
    cancelled: int

    @classmethod
    def from_jobs(cls, jobs: list[TranscriptionJob]) -> "QueueStats":
        counts = {s: 0 for s in JobStatus}
        for job in jobs:
            counts[job.status] = counts.get(job.status, 0) + 1
        return cls(
            total=len(jobs),
            waiting=counts.get(JobStatus.WAITING, 0),
            processing=counts.get(JobStatus.PROCESSING, 0),
            completed=counts.get(JobStatus.COMPLETED, 0),
            errors=counts.get(JobStatus.ERROR, 0),
            cancelled=counts.get(JobStatus.CANCELLED, 0),
        )


class QueueManager:
    def __init__(
        self,
        settings: SettingsService,
        on_job_updated: Optional[JobCallback] = None,
        on_queue_idle: Optional[VoidCallback] = None,
        on_status_message: Optional[Callable[[str], None]] = None,
        on_progress: Optional[ProgressCallback] = None,
    ) -> None:
        self.settings = settings
        self._jobs: list[TranscriptionJob] = []
        self._selected_id: Optional[str] = None
        self._on_job_updated = on_job_updated
        self._on_queue_idle = on_queue_idle
        self._on_status_message = on_status_message
        self._on_progress = on_progress
        self._transcription = TranscriptionService()
        self._extraction = ExtractionService()
        self._export = ExportService()
        self._logger = get_logger()
        self._worker: Optional[threading.Thread] = None
        self._stop_requested = False
        self._processing = False
        self._start_lock = threading.Lock()
        self._session_completed = 0
        self._session_errors = 0

    @property
    def jobs(self) -> list[TranscriptionJob]:
        return list(self._jobs)

    @property
    def is_processing(self) -> bool:
        return self._processing

    @property
    def stats(self) -> QueueStats:
        return QueueStats.from_jobs(self._jobs)

    @property
    def selected_job(self) -> Optional[TranscriptionJob]:
        if not self._selected_id:
            return None
        return self._get_job(self._selected_id)

    def get_overall_progress(self) -> float:
        """Progresso da sessão atual: itens finalizados / itens elegíveis."""
        stats = self.stats
        if not self._processing and stats.total == 0:
            return 0.0
        eligible = stats.completed + stats.errors + stats.cancelled + stats.processing + stats.waiting
        if eligible == 0:
            return 0.0
        done = stats.completed + stats.errors + stats.cancelled
        if stats.processing:
            return min(0.99, (done + 0.5) / eligible)
        return done / eligible if eligible else 0.0

    def select_job(self, job_id: Optional[str]) -> None:
        self._selected_id = job_id

    def add_files(self, paths: list[str]) -> list[TranscriptionJob]:
        added: list[TranscriptionJob] = []
        for path in paths:
            path = path.strip().strip('"')
            if not path or not os.path.isfile(path):
                self._logger.warning("Arquivo ignorado (inexistente): %s", path)
                continue
            job = TranscriptionJob(file_path=path)
            if not job.is_supported():
                info = classify_job_error(
                    ValueError("Tipo de arquivo não suportado."), path
                )
                job.status = JobStatus.ERROR
                job.error_message = info.user_message
                job.error_code = info.error_code
                self._logger.error("Tipo não suportado: %s", path)
            output_dir = self.settings.resolve_output_dir(path)
            fmt = self.settings.default_export_format  # type: ignore[arg-type]
            job.output_path = ExportService.build_output_path(path, output_dir, fmt)
            self._jobs.append(job)
            added.append(job)
            self._notify(job)
        self._emit_progress()
        return added

    def remove_selected(self) -> bool:
        job = self.selected_job
        if not job:
            return False
        if job.status == JobStatus.PROCESSING:
            return False
        self._jobs = [j for j in self._jobs if j.id != job.id]
        if self._selected_id == job.id:
            self._selected_id = None
        self._emit_progress()
        return True

    def clear_queue(self) -> None:
        if self._processing:
            self._jobs = [j for j in self._jobs if j.status == JobStatus.PROCESSING]
        else:
            self._jobs = []
            self._selected_id = None
        self._emit_progress()

    def start_queue(self) -> bool:
        with self._start_lock:
            if self._processing:
                self._emit_status("A fila já está em processamento.")
                self._logger.warning("Tentativa de iniciar fila duplicada ignorada.")
                return False
            pending = [j for j in self._jobs if j.status in (JobStatus.WAITING, JobStatus.ERROR)]
            if not pending:
                self._emit_status("Nenhum item aguardando na fila.")
                return False
            self._stop_requested = False
            self._processing = True
            self._session_completed = 0
            self._session_errors = 0
            self._worker = threading.Thread(target=self._process_queue, daemon=True)
            self._worker.start()
            self._logger.info("Fila iniciada com %d item(ns) pendente(s).", len(pending))
            self._emit_progress()
            return True

    def cancel_queue(self) -> bool:
        if not self._processing:
            self._emit_status("Nenhuma fila em processamento.")
            return False
        self._stop_requested = True
        self._emit_status("Cancelando fila após o item atual…")
        self._logger.info("Cancelamento de fila solicitado.")
        return True

    def resolve_output_folder_for_job(self, job: Optional[TranscriptionJob]) -> Optional[str]:
        if job and job.output_path:
            folder = os.path.dirname(os.path.abspath(job.output_path))
            if os.path.isdir(folder):
                return folder
        if job:
            folder = self.settings.resolve_output_dir(job.file_path)
            if os.path.isdir(folder):
                return folder
        folder = self.settings.output_folder.strip()
        if folder and os.path.isdir(folder):
            return folder
        return None

    def _process_queue(self) -> None:
        cancelled_count = 0
        try:
            for job in list(self._jobs):
                if self._stop_requested:
                    if job.status == JobStatus.WAITING:
                        job.status = JobStatus.CANCELLED
                        job.error_message = "Cancelado pelo usuário."
                        cancelled_count += 1
                        self._notify(job)
                    continue
                if job.status not in (JobStatus.WAITING, JobStatus.ERROR):
                    continue
                self._process_job(job)
                self._emit_progress()
        finally:
            was_cancelled = self._stop_requested
            self._processing = False
            self._stop_requested = False

            if was_cancelled and (self._session_completed or self._session_errors or cancelled_count):
                self.settings.add_partial_queue_history(
                    self._session_completed,
                    self._session_errors,
                    cancelled_count,
                    self.stats.total,
                    reason="cancelada",
                )

            self._emit_progress()
            if self._on_queue_idle:
                self._on_queue_idle()
            msg = "Fila cancelada." if was_cancelled else "Fila finalizada."
            self._emit_status(msg)
            self._logger.info(msg)

    def _process_job(self, job: TranscriptionJob) -> None:
        if self._stop_requested:
            return

        job.status = JobStatus.PROCESSING
        job.error_message = ""
        job.error_code = ""
        self._notify(job)
        self._emit_status(f"Processando: {job.file_name}")
        self._logger.info("Processando job: %s (%s)", job.file_name, job.file_type)

        try:
            if not os.path.isfile(job.file_path):
                raise FileNotFoundError(job.file_path)

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

            if self._stop_requested:
                job.status = JobStatus.CANCELLED
                job.error_message = "Cancelado durante o processamento."
                return

            job.result_text = text
            output_dir = self.settings.resolve_output_dir(job.file_path)
            fmt = self.settings.default_export_format  # type: ignore[arg-type]
            job.output_path = self._export.save_auto(job.file_path, text, output_dir, fmt)
            job.status = JobStatus.COMPLETED
            self._session_completed += 1
            self.settings.add_history_entry(
                job.file_name,
                job.file_type,
                status="concluído",
                output_path=job.output_path,
            )
            self._logger.info("Concluído: %s -> %s", job.file_name, job.output_path)
        except Exception as exc:
            info = classify_job_error(exc, job.file_path)
            job.status = JobStatus.ERROR
            job.error_message = info.user_message
            job.error_code = info.error_code
            job.result_text = ""
            self._session_errors += 1
            self.settings.add_history_entry(
                job.file_name,
                job.file_type,
                status="erro",
                message=info.user_message,
            )
            self._logger.error(
                "Erro no job %s [%s]: %s\n%s",
                job.file_name,
                info.error_code,
                info.user_message,
                format_traceback(exc),
            )

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

    def _emit_progress(self) -> None:
        if self._on_progress:
            self._on_progress(self.get_overall_progress(), self.stats)
