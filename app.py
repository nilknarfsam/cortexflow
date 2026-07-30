"""Ponto de entrada do CortexFlow."""

from __future__ import annotations

import multiprocessing
import os
import sys
from pathlib import Path

from src.core.windows_subprocess import configure_windowless_subprocesses

configure_windowless_subprocesses()


def inject_local_binaries_to_path() -> None:
    """
    Prioriza FFmpeg/Tesseract embutidos em ``bin/`` antes do PATH do sistema.

    Deve rodar antes de imports que invocam Whisper, ffmpeg ou pytesseract.
    """
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
        candidates = (
            base / "bin",
            Path(sys.executable).resolve().parent / "bin",
            Path(sys.executable).resolve().parent / "_internal" / "bin",
        )
    else:
        candidates = (Path(__file__).resolve().parent / "bin",)

    for bin_dir in candidates:
        if not bin_dir.is_dir():
            continue
        path_entry = str(bin_dir.resolve())
        os.environ["PATH"] = path_entry + os.pathsep + os.environ.get("PATH", "")
        break


inject_local_binaries_to_path()


def run_frozen_smoke_test() -> int:
    """Valida imports e binários essenciais sem inicializar a interface."""
    try:
        import customtkinter  # noqa: F401
        import tkinterdnd2  # noqa: F401
        import torch  # noqa: F401
        import whisper  # noqa: F401

        if getattr(sys, "frozen", False):
            executable_dir = Path(sys.executable).resolve().parent
            binary_dirs = (
                executable_dir / "bin",
                executable_dir / "_internal" / "bin",
            )
            if not any(
                (directory / "ffmpeg.exe").is_file()
                and (directory / "ffprobe.exe").is_file()
                for directory in binary_dirs
            ):
                return 2
    except Exception:
        return 1
    return 0


def main() -> int:
    multiprocessing.freeze_support()
    if "--smoke-test" in sys.argv:
        return run_frozen_smoke_test()

    from src.ui.main_window import run_app

    run_app()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
