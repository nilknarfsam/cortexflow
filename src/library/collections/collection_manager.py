"""Gerenciamento de coleções de conhecimento."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.core.settings_service import DATA_DIR

LIBRARY_DIR = DATA_DIR / "library"
COLLECTIONS_FILE = LIBRARY_DIR / "collections.json"

DEFAULT_COLLECTIONS = (
    "Teologia",
    "Engenharia",
    "Podcasts",
    "Reuniões",
    "Cursos",
    "Devocionais",
    "Estudos",
    "Pesquisas",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(name: str) -> str:
    base = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")
    while "--" in base:
        base = base.replace("--", "-")
    return base[:48] or "collection"


class CollectionManager:
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}
        LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
        self.load()
        self._ensure_defaults()

    def load(self) -> None:
        if not COLLECTIONS_FILE.exists():
            self._items = {}
            return
        try:
            with open(COLLECTIONS_FILE, encoding="utf-8") as f:
                data = json.load(f)
            raw = data.get("items", data) if isinstance(data, dict) else {}
            self._items = raw if isinstance(raw, dict) else {}
        except (json.JSONDecodeError, OSError, TypeError):
            self._items = {}

    def save(self) -> None:
        LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
        with open(COLLECTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "items": self._items}, f, ensure_ascii=False, indent=2)

    def _ensure_defaults(self) -> None:
        if self._items:
            return
        for name in DEFAULT_COLLECTIONS:
            self.create(name, description=f"Coleção padrão: {name}")
        self.save()

    @property
    def all(self) -> list[dict[str, Any]]:
        return [dict(v) for v in self._items.values()]

    def get(self, collection_id: str) -> dict[str, Any] | None:
        item = self._items.get(collection_id)
        return dict(item) if isinstance(item, dict) else None

    def get_by_name(self, name: str) -> dict[str, Any] | None:
        name_l = name.strip().lower()
        for item in self._items.values():
            if str(item.get("name", "")).lower() == name_l:
                return dict(item)
        return None

    def create(
        self,
        name: str,
        *,
        description: str = "",
        tags: list[str] | None = None,
        workspace_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        existing = self.get_by_name(name)
        if existing:
            return existing
        cid = f"col-{_slug(name)}-{uuid.uuid4().hex[:6]}"
        now = _utc_now()
        entry = {
            "id": cid,
            "name": name.strip(),
            "description": description.strip(),
            "tags": list(tags or []),
            "workspace_ids": list(workspace_ids or []),
            "created_at": now,
            "updated_at": now,
        }
        self._items[cid] = entry
        self.save()
        return entry

    def update(self, collection_id: str, **fields: Any) -> dict[str, Any] | None:
        item = self._items.get(collection_id)
        if not item:
            return None
        for key in ("name", "description", "tags", "workspace_ids"):
            if key in fields and fields[key] is not None:
                item[key] = fields[key]
        item["updated_at"] = _utc_now()
        self.save()
        return dict(item)

    def list_names(self) -> list[str]:
        return sorted(str(v.get("name", "")) for v in self._items.values() if v.get("name"))

    def list_ids(self) -> list[str]:
        return list(self._items.keys())
