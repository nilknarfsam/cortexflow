"""Métricas de performance do pipeline — tempos por estágio."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PerformanceMetrics:
    whisper_seconds: float = 0.0
    ocr_seconds: float = 0.0
    semantic_seconds: float = 0.0
    export_seconds: float = 0.0
    total_seconds: float = 0.0
    cache_hit: bool = False
    reused_pipeline: bool = False

    _started_at: float = field(default=0.0, repr=False)
    _whisper_start: float = field(default=0.0, repr=False)
    _ocr_start: float = field(default=0.0, repr=False)
    _semantic_start: float = field(default=0.0, repr=False)
    _export_start: float = field(default=0.0, repr=False)

    def start_total(self) -> None:
        self._started_at = time.perf_counter()

    def finish_total(self) -> None:
        if self._started_at:
            self.total_seconds = time.perf_counter() - self._started_at

    def start_whisper(self) -> None:
        self._whisper_start = time.perf_counter()

    def stop_whisper(self) -> None:
        if self._whisper_start:
            self.whisper_seconds += time.perf_counter() - self._whisper_start
            self._whisper_start = 0.0

    def start_ocr(self) -> None:
        self._ocr_start = time.perf_counter()

    def stop_ocr(self) -> None:
        if self._ocr_start:
            self.ocr_seconds += time.perf_counter() - self._ocr_start
            self._ocr_start = 0.0

    def start_semantic(self) -> None:
        self._semantic_start = time.perf_counter()

    def stop_semantic(self) -> None:
        if self._semantic_start:
            self.semantic_seconds += time.perf_counter() - self._semantic_start
            self._semantic_start = 0.0

    def start_export(self) -> None:
        self._export_start = time.perf_counter()

    def stop_export(self) -> None:
        if self._export_start:
            self.export_seconds += time.perf_counter() - self._export_start
            self._export_start = 0.0

    def to_history_fields(self) -> dict[str, str]:
        return {
            "processing_time": f"{self.total_seconds:.2f}s",
            "tempo_whisper": f"{self.whisper_seconds:.2f}s",
            "tempo_ocr": f"{self.ocr_seconds:.2f}s",
            "tempo_semantic": f"{self.semantic_seconds:.2f}s",
            "tempo_export": f"{self.export_seconds:.2f}s",
            "cache_hit": "sim" if self.cache_hit else "não",
            "reused_pipeline": "sim" if self.reused_pipeline else "não",
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "whisper_seconds": round(self.whisper_seconds, 3),
            "ocr_seconds": round(self.ocr_seconds, 3),
            "semantic_seconds": round(self.semantic_seconds, 3),
            "export_seconds": round(self.export_seconds, 3),
            "total_seconds": round(self.total_seconds, 3),
            "cache_hit": self.cache_hit,
            "reused_pipeline": self.reused_pipeline,
        }
