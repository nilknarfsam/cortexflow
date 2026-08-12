"""Exportação consolidada dos artefatos de dataset."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.datasets.registry.dataset_registry import (
    CHUNK_DATASETS_FILE,
    DATASETS_DIR,
    KNOWLEDGE_DATASETS_FILE,
    KNOWLEDGE_INDEX_FILE,
    DatasetRegistry,
)
from src.datasets.statistics.dataset_stats import compute_dataset_statistics
from src.datasets.validators.dataset_validator import DatasetValidator

VALIDATION_REPORT_FILE = DATASETS_DIR / "dataset_validation_report.json"
STATISTICS_FILE = DATASETS_DIR / "dataset_statistics.json"


class DatasetExporter:
    def __init__(self, registry: DatasetRegistry | None = None) -> None:
        from src.datasets.registry.dataset_registry import get_dataset_registry

        self._registry = registry or get_dataset_registry()

    def export_all(self) -> dict[str, str]:
        """Garante persistência dos JSON em data/datasets/."""
        paths: dict[str, str] = {}
        self._registry.load()
        paths["knowledge_datasets"] = str(KNOWLEDGE_DATASETS_FILE)
        paths["chunk_datasets"] = str(CHUNK_DATASETS_FILE)
        paths["knowledge_index"] = str(KNOWLEDGE_INDEX_FILE)

        stats = compute_dataset_statistics(
            self._registry.knowledge_datasets,
            self._registry.chunk_datasets,
            self._registry.knowledge_index,
        )
        self._write_json(STATISTICS_FILE, stats.to_dict())
        paths["dataset_statistics"] = str(STATISTICS_FILE)

        report = DatasetValidator().validate_all(
            self._registry.knowledge_datasets,
            self._registry.chunk_datasets,
            self._registry.knowledge_index,
        )
        self._write_json(VALIDATION_REPORT_FILE, report.to_dict())
        paths["dataset_validation_report"] = str(VALIDATION_REPORT_FILE)
        return paths

    def export_dataset_copy(self, dataset_id: str, dest_dir: Path) -> str | None:
        ds = self._registry.get_knowledge(dataset_id)
        if not ds:
            return None
        dest_dir.mkdir(parents=True, exist_ok=True)
        path = dest_dir / f"{dataset_id}.json"
        self._write_json(path, ds)
        return str(path)

    @staticmethod
    def _write_json(path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
