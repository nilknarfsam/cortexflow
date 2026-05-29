from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
TEXT_EXTENSIONS = {".txt"}
DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".xlsx"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

SUPPORTED_EXTENSIONS = (
    AUDIO_EXTENSIONS
    | VIDEO_EXTENSIONS
    | TEXT_EXTENSIONS
    | DOCUMENT_EXTENSIONS
    | IMAGE_EXTENSIONS
)


class JobStatus(str, Enum):
    WAITING = "aguardando"
    PROCESSING = "processando"
    COMPLETED = "concluído"
    ERROR = "erro"
    CANCELLED = "cancelado"


def detect_file_type(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in AUDIO_EXTENSIONS:
        return "áudio"
    if ext in VIDEO_EXTENSIONS:
        return "vídeo"
    if ext in TEXT_EXTENSIONS:
        return "texto"
    if ext == ".pdf":
        return "pdf"
    if ext == ".docx":
        return "docx"
    if ext == ".xlsx":
        return "xlsx"
    if ext in IMAGE_EXTENSIONS:
        return "imagem"
    return "desconhecido"


@dataclass
class TranscriptionJob:
    file_path: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = JobStatus.WAITING
    output_path: str = ""
    result_text: str = ""
    error_message: str = ""
    error_code: str = ""
    semantic_metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def file_name(self) -> str:
        return os.path.basename(self.file_path)

    @property
    def file_type(self) -> str:
        return detect_file_type(self.file_path)

    @property
    def extension(self) -> str:
        return os.path.splitext(self.file_path)[1].lower()

    def is_supported(self) -> bool:
        return self.extension in SUPPORTED_EXTENSIONS
