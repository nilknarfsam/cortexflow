"""Validação de integridade dos datasets."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

KNOWLEDGE_REQUIRED = (
    "dataset_id",
    "document_id",
    "title",
    "workspace",
    "collection",
    "topics",
    "references",
    "chunks",
    "metadata",
)

CHUNK_REQUIRED = (
    "chunk_id",
    "document_id",
    "workspace",
    "collection",
    "topics",
    "references",
    "content",
    "metadata",
)


@dataclass
class ValidationReport:
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    datasets_checked: int = 0
    chunks_checked: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "datasets_checked": self.datasets_checked,
            "chunks_checked": self.chunks_checked,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


class DatasetValidator:
    def validate_all(
        self,
        knowledge_datasets: dict[str, dict[str, Any]],
        chunk_datasets: dict[str, dict[str, Any]],
        knowledge_index: dict[str, Any] | None = None,
    ) -> ValidationReport:
        report = ValidationReport()
        seen_dataset_ids: set[str] = set()
        seen_doc_ids: set[str] = set()
        chunk_ids: set[str] = set()

        for ds_id, ds in knowledge_datasets.items():
            report.datasets_checked += 1
            self._check_required(ds, KNOWLEDGE_REQUIRED, f"knowledge[{ds_id}]", report)
            rid = str(ds.get("dataset_id", ""))
            if rid in seen_dataset_ids:
                report.errors.append(f"dataset_id duplicado: {rid}")
                report.valid = False
            seen_dataset_ids.add(rid)

            doc_id = str(ds.get("document_id", ""))
            if doc_id in seen_doc_ids:
                report.warnings.append(f"document_id repetido em datasets: {doc_id}")
            seen_doc_ids.add(doc_id)

            doc_chunks = {str(c.get("chunk_id") or c.get("id", "")) for c in (ds.get("chunks") or [])}
            for cid in doc_chunks:
                if cid and cid not in chunk_datasets:
                    report.warnings.append(
                        f"chunk {cid} referenciado em {ds_id} ausente em chunk_datasets"
                    )

        for ch_id, ch in chunk_datasets.items():
            report.chunks_checked += 1
            self._check_required(ch, CHUNK_REQUIRED, f"chunk[{ch_id}]", report)
            cid = str(ch.get("chunk_id", ""))
            if cid in chunk_ids:
                report.errors.append(f"chunk_id duplicado: {cid}")
                report.valid = False
            chunk_ids.add(cid)

            doc_id = str(ch.get("document_id", ""))
            if doc_id and doc_id not in seen_doc_ids:
                report.warnings.append(f"chunk {cid} referencia documento ausente: {doc_id}")

        if knowledge_index:
            for key in (
                "topics_index",
                "references_index",
                "authors_index",
                "speakers_index",
                "collections_index",
                "workspaces_index",
            ):
                if key not in knowledge_index:
                    report.warnings.append(f"índice ausente: {key}")

        if report.errors:
            report.valid = False
        return report

    @staticmethod
    def _check_required(
        record: dict[str, Any],
        fields: tuple[str, ...],
        label: str,
        report: ValidationReport,
    ) -> None:
        for field in fields:
            if field not in record:
                report.errors.append(f"{label}: campo obrigatório ausente '{field}'")
                report.valid = False
