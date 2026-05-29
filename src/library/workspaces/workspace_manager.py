"""Gerenciamento de workspaces — bibliotecas contextuais separadas."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.core.settings_service import DATA_DIR

LIBRARY_DIR = DATA_DIR / "library"
WORKSPACES_FILE = LIBRARY_DIR / "workspaces.json"

DEFAULT_WORKSPACE_ID = "ws-default"
DEFAULT_WORKSPACE_NAME = "Biblioteca Principal"

PRESET_WORKSPACES = (
    ("ws-renascer", "Instituto Renascer"),
    ("ws-estudos-ga", "Estudos GA"),
    ("ws-ict", "Engenharia ICT"),
    ("ws-franklin", "Biblioteca Franklin"),
    ("ws-cursos", "Cursos Online"),
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorkspaceManager:
    def __init__(self) -> None:
        self._items: dict[str, dict[str, Any]] = {}
        LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
        self.load()
        self._ensure_defaults()

    def load(self) -> None:
        if not WORKSPACES_FILE.exists():
            self._items = {}
            return
        try:
            with open(WORKSPACES_FILE, encoding="utf-8") as f:
                data = json.load(f)
            raw = data.get("items", data) if isinstance(data, dict) else {}
            self._items = raw if isinstance(raw, dict) else {}
        except (json.JSONDecodeError, OSError, TypeError):
            self._items = {}

    def save(self) -> None:
        LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
        with open(WORKSPACES_FILE, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "items": self._items}, f, ensure_ascii=False, indent=2)

    def _ensure_defaults(self) -> None:
        if DEFAULT_WORKSPACE_ID not in self._items:
            now = _utc_now()
            self._items[DEFAULT_WORKSPACE_ID] = {
                "id": DEFAULT_WORKSPACE_ID,
                "name": DEFAULT_WORKSPACE_NAME,
                "description": "Workspace padrão do CortexFlow",
                "collection_ids": [],
                "metadata": {},
                "created_at": now,
                "updated_at": now,
            }
        for ws_id, name in PRESET_WORKSPACES:
            if ws_id not in self._items:
                now = _utc_now()
                self._items[ws_id] = {
                    "id": ws_id,
                    "name": name,
                    "description": "",
                    "collection_ids": [],
                    "metadata": {},
                    "created_at": now,
                    "updated_at": now,
                }
        self.save()

    @property
    def all(self) -> list[dict[str, Any]]:
        return [dict(v) for v in self._items.values()]

    def get(self, workspace_id: str) -> dict[str, Any] | None:
        item = self._items.get(workspace_id)
        return dict(item) if isinstance(item, dict) else None

    def get_default_id(self) -> str:
        return DEFAULT_WORKSPACE_ID

    def create(
        self,
        name: str,
        *,
        description: str = "",
        collection_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        ws_id = f"ws-{uuid.uuid4().hex[:10]}"
        now = _utc_now()
        entry = {
            "id": ws_id,
            "name": name.strip(),
            "description": description.strip(),
            "collection_ids": list(collection_ids or []),
            "metadata": dict(metadata or {}),
            "created_at": now,
            "updated_at": now,
        }
        self._items[ws_id] = entry
        self.save()
        return entry

    def update(self, workspace_id: str, **fields: Any) -> dict[str, Any] | None:
        item = self._items.get(workspace_id)
        if not item:
            return None
        for key in ("name", "description", "collection_ids", "metadata"):
            if key in fields and fields[key] is not None:
                item[key] = fields[key]
        item["updated_at"] = _utc_now()
        self.save()
        return dict(item)

    def link_collection(self, workspace_id: str, collection_id: str) -> None:
        item = self._items.get(workspace_id)
        if not item:
            return
        ids = list(item.get("collection_ids", []))
        if collection_id not in ids:
            ids.append(collection_id)
            item["collection_ids"] = ids
            item["updated_at"] = _utc_now()
            self.save()

    def list_names(self) -> list[tuple[str, str]]:
        return [(str(v["id"]), str(v.get("name", ""))) for v in self._items.values()]
