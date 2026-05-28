from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"
HISTORY_FILE = DATA_DIR / "historico_transcricoes.json"
LEGACY_HISTORY_FILE = PROJECT_ROOT / "historico_transcricoes.json"

DEFAULT_SETTINGS: dict[str, Any] = {
    "theme": "System",
    "language": "auto",
    "output_folder": "",
    "default_export_format": "txt",
    "export_mode": "raw",
    "content_template": "generic",
    "whisper_model": "base",
    "max_history": 10,
}


class SettingsService:
    def __init__(self) -> None:
        self._settings = dict(DEFAULT_SETTINGS)
        self._history: list[dict[str, str]] = []
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_history()
        self.load()

    def _migrate_legacy_history(self) -> None:
        if LEGACY_HISTORY_FILE.exists() and not HISTORY_FILE.exists():
            shutil.copy2(LEGACY_HISTORY_FILE, HISTORY_FILE)

    def load(self) -> None:
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, encoding="utf-8") as f:
                    loaded = json.load(f)
                self._settings.update({k: loaded[k] for k in DEFAULT_SETTINGS if k in loaded})
            except (json.JSONDecodeError, OSError):
                pass
        self._history = self._load_history_file()

    def save_settings(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, ensure_ascii=False, indent=2)

    def _load_history_file(self) -> list[dict[str, str]]:
        if not HISTORY_FILE.exists():
            return []
        try:
            with open(HISTORY_FILE, encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def save_history(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self._history, f, ensure_ascii=False, indent=2)

    @property
    def theme(self) -> str:
        return str(self._settings["theme"])

    @theme.setter
    def theme(self, value: str) -> None:
        self._settings["theme"] = value
        self.save_settings()

    @property
    def language(self) -> str:
        return str(self._settings["language"])

    @language.setter
    def language(self, value: str) -> None:
        self._settings["language"] = value
        self.save_settings()

    @property
    def output_folder(self) -> str:
        return str(self._settings["output_folder"])

    @output_folder.setter
    def output_folder(self, value: str) -> None:
        self._settings["output_folder"] = value
        self.save_settings()

    @property
    def default_export_format(self) -> str:
        return str(self._settings["default_export_format"])

    @default_export_format.setter
    def default_export_format(self, value: str) -> None:
        self._settings["default_export_format"] = value
        self.save_settings()

    @property
    def export_mode(self) -> str:
        return str(self._settings.get("export_mode", "raw"))

    @export_mode.setter
    def export_mode(self, value: str) -> None:
        self._settings["export_mode"] = value
        self.save_settings()

    @property
    def content_template(self) -> str:
        return str(self._settings.get("content_template", "generic"))

    @content_template.setter
    def content_template(self, value: str) -> None:
        self._settings["content_template"] = value
        self.save_settings()

    @property
    def whisper_model(self) -> str:
        return str(self._settings["whisper_model"])

    @whisper_model.setter
    def whisper_model(self, value: str) -> None:
        self._settings["whisper_model"] = value
        self.save_settings()

    @property
    def max_history(self) -> int:
        return int(self._settings["max_history"])

    @property
    def history(self) -> list[dict[str, str]]:
        return list(self._history)

    def add_history_entry(
        self,
        file_name: str,
        file_type: str,
        *,
        status: str = "concluído",
        message: str = "",
        output_path: str = "",
        export_mode: str = "",
        template_usado: str = "",
        pipeline_stage: str = "",
        tipo_documento: str = "",
    ) -> None:
        entry: dict[str, str] = {
            "arquivo": file_name,
            "tipo": file_type,
            "status": status,
        }
        if message:
            entry["mensagem"] = message
        if output_path:
            entry["saida"] = output_path
        if export_mode:
            entry["export_mode"] = export_mode
        if template_usado:
            entry["template_usado"] = template_usado
        if pipeline_stage:
            entry["pipeline_stage"] = pipeline_stage
        if tipo_documento:
            entry["tipo_documento"] = tipo_documento
        self._history.append(entry)
        max_items = self.max_history
        if len(self._history) > max_items:
            self._history = self._history[-max_items:]
        self.save_history()

    def add_partial_queue_history(
        self,
        completed: int,
        errors: int,
        cancelled: int,
        total: int,
        *,
        reason: str = "cancelada",
    ) -> None:
        self.add_history_entry(
            f"Fila ({completed}/{total})",
            "sessão",
            status="parcial",
            message=(
                f"Fila {reason}: {completed} concluído(s), "
                f"{errors} erro(s), {cancelled} não processado(s)."
            ),
        )

    def resolve_output_dir(self, source_path: str) -> str:
        folder = self.output_folder.strip()
        if folder and os.path.isdir(folder):
            return folder
        return os.path.dirname(os.path.abspath(source_path))
