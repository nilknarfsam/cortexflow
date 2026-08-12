"""Diagnóstico local e sanitizado das dependências do CortexFlow."""

from __future__ import annotations

import importlib.metadata
import platform
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from src.core.settings_service import DATA_DIR
from src.version import APP_NAME, APP_VERSION


@dataclass(frozen=True)
class ComponentDiagnostic:
    name: str
    available: bool
    version: str = ""
    detail: str = ""

    @property
    def status_label(self) -> str:
        return "OK" if self.available else "AUSENTE"


@dataclass(frozen=True)
class EnvironmentDiagnosticReport:
    generated_at: str
    python_version: str
    operating_system: str
    data_writable: bool
    components: tuple[ComponentDiagnostic, ...]

    @property
    def healthy(self) -> bool:
        required = {"FFmpeg", "FFprobe", "Whisper"}
        return self.data_writable and all(
            item.available for item in self.components if item.name in required
        )

    def to_safe_text(self) -> str:
        """Texto para suporte sem caminhos locais, documentos ou credenciais."""
        lines = [
            f"{APP_NAME} {APP_VERSION}",
            f"Gerado em: {self.generated_at}",
            f"Python: {self.python_version}",
            f"Sistema: {self.operating_system}",
            f"Pasta de dados gravável: {'sim' if self.data_writable else 'não'}",
            "",
            "Componentes:",
        ]
        for item in self.components:
            suffix = f" ({item.version})" if item.version else ""
            detail = f" — {item.detail}" if item.detail else ""
            lines.append(f"- {item.name}: {item.status_label}{suffix}{detail}")
        lines.append("")
        lines.append(f"Estado geral: {'OK' if self.healthy else 'ATENÇÃO'}")
        return "\n".join(lines)


def _first_version_line(command: str) -> ComponentDiagnostic:
    executable = shutil.which(command)
    display_name = {
        "ffmpeg": "FFmpeg",
        "ffprobe": "FFprobe",
        "tesseract": "Tesseract",
    }[command]
    if not executable:
        optional = command == "tesseract"
        detail = "opcional; necessário para OCR" if optional else "não encontrado no PATH"
        return ComponentDiagnostic(display_name, False, detail=detail)

    try:
        completed = subprocess.run(
            [executable, "-version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        output = completed.stdout or completed.stderr
        first_line = output.splitlines()[0].strip() if output else ""
        version = _extract_binary_version(command, first_line)
        if completed.returncode == 0:
            return ComponentDiagnostic(display_name, True, version=version)
        return ComponentDiagnostic(
            display_name,
            False,
            version=version,
            detail=f"retorno {completed.returncode}",
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return ComponentDiagnostic(
            display_name,
            False,
            detail=f"falha ao executar: {type(exc).__name__}",
        )


def _extract_binary_version(command: str, first_line: str) -> str:
    parts = first_line.split()
    if command in {"ffmpeg", "ffprobe"} and len(parts) >= 3:
        return parts[2]
    if command == "tesseract" and len(parts) >= 2:
        return parts[1]
    return ""


def _package_diagnostic(distribution: str, display_name: str) -> ComponentDiagnostic:
    try:
        version = importlib.metadata.version(distribution)
        return ComponentDiagnostic(display_name, True, version=version)
    except importlib.metadata.PackageNotFoundError:
        return ComponentDiagnostic(display_name, False, detail="pacote Python ausente")


def _whisper_model_diagnostic(
    model_name: str = "base",
    *,
    cache_dir: Path | None = None,
) -> ComponentDiagnostic:
    target_dir = cache_dir or (Path.home() / ".cache" / "whisper")
    model_file = target_dir / f"{model_name}.pt"
    if model_file.is_file() and model_file.stat().st_size > 0:
        return ComponentDiagnostic(
            f"Modelo Whisper ({model_name})",
            True,
            detail="disponível localmente",
        )
    return ComponentDiagnostic(
        f"Modelo Whisper ({model_name})",
        False,
        detail="será baixado no primeiro uso",
    )


def _can_write_data_dir(data_dir: Path) -> bool:
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=data_dir, prefix=".diagnostic-", delete=True):
            pass
        return True
    except OSError:
        return False


def collect_environment_diagnostics(
    *,
    data_dir: Path | None = None,
) -> EnvironmentDiagnosticReport:
    """Coleta apenas informações técnicas necessárias para diagnóstico local."""
    target_data_dir = Path(data_dir) if data_dir is not None else DATA_DIR
    components = (
        _first_version_line("ffmpeg"),
        _first_version_line("ffprobe"),
        _first_version_line("tesseract"),
        _package_diagnostic("openai-whisper", "Whisper"),
        _package_diagnostic("torch", "PyTorch"),
        _whisper_model_diagnostic("base"),
    )
    return EnvironmentDiagnosticReport(
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        python_version=platform.python_version(),
        operating_system=f"{platform.system()} {platform.release()} ({platform.machine()})",
        data_writable=_can_write_data_dir(target_data_dir),
        components=components,
    )
