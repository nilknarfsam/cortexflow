"""Utilitários de caminhos para drag-and-drop e diálogos de arquivo."""

from __future__ import annotations

import os

from src.models.transcription_job import SUPPORTED_EXTENSIONS

_WINDOWS_MAX_PATH = 260


def normalized_path_length(path: str) -> int:
    """Comprimento do caminho absoluto normalizado (relevante no limite MAX_PATH do Windows)."""
    return len(os.path.normpath(os.path.abspath(path)))


def check_windows_path_limits(*paths: str) -> str | None:
    """Retorna mensagem em PT-BR se algum caminho excede ``MAX_PATH`` no Windows."""
    if os.name != "nt":
        return None
    for path in paths:
        if not path:
            continue
        length = normalized_path_length(path)
        if length >= _WINDOWS_MAX_PATH:
            return (
                f"Caminho muito longo para o Windows ({length} caracteres, "
                f"máximo {_WINDOWS_MAX_PATH - 1}): {os.path.basename(path)}"
            )
    return None


def unsupported_file_reason(path: str) -> str | None:
    """Motivo pelo qual o arquivo não é suportado, ou ``None`` se válido."""
    ext = os.path.splitext(path)[1].lower()
    if not ext:
        return "Arquivo sem extensão não suportado."
    if ext not in SUPPORTED_EXTENSIONS:
        return f"Tipo de arquivo não suportado: {ext}"
    return None


def validate_job_paths(source_path: str, output_path: str = "") -> None:
    """Valida extensão e limites de caminho; levanta ``ValueError`` com mensagem amigável."""
    reason = unsupported_file_reason(source_path)
    if reason:
        raise ValueError(reason)
    msg = check_windows_path_limits(source_path, output_path)
    if msg:
        raise ValueError(msg)


def parse_dropped_paths(data: str) -> list[str]:
    """Interpreta caminhos do drag-and-drop no Windows (com ou sem chaves)."""
    data = data.strip()
    if not data:
        return []

    paths: list[str] = []
    current: list[str] = []
    in_braces = False

    for char in data:
        if char == "{":
            in_braces = True
            current = []
        elif char == "}":
            in_braces = False
            path = "".join(current).strip()
            if path:
                paths.append(path)
            current = []
        elif char == " " and not in_braces:
            path = "".join(current).strip()
            if path:
                paths.append(path)
            current = []
        else:
            current.append(char)

    remainder = "".join(current).strip()
    if remainder:
        paths.append(remainder)

    if not paths:
        cleaned = data.replace("{", "").replace("}", "").strip()
        if cleaned:
            paths = [cleaned]

    return [p for p in paths if os.path.isfile(p)]


def collect_supported_files(folder: str) -> list[str]:
    """Lista arquivos suportados recursivamente em uma pasta."""
    paths: list[str] = []
    folder = folder.strip().strip('"')
    if not folder or not os.path.isdir(folder):
        return paths
    for root, _dirs, files in os.walk(folder):
        for name in files:
            path = os.path.join(root, name)
            ext = os.path.splitext(path)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                paths.append(path)
    return paths


FILE_DIALOG_TYPES = [
    (
        "Todos suportados",
        "*.mp3 *.wav *.m4a *.flac *.mp4 *.avi *.mov *.mkv *.txt *.pdf *.docx *.xlsx *.jpg *.jpeg *.png",
    ),
    ("Áudio", "*.mp3 *.wav *.m4a *.flac"),
    ("Vídeo", "*.mp4 *.avi *.mov *.mkv"),
    ("Texto", "*.txt"),
    ("PDF", "*.pdf"),
    ("Word DOCX", "*.docx"),
    ("Planilha Excel", "*.xlsx"),
    ("Imagem", "*.jpg *.jpeg *.png"),
    ("Todos os arquivos", "*.*"),
]
