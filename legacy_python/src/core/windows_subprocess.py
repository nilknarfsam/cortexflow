"""Configuração de subprocessos sem janela de console no Windows."""

from __future__ import annotations

import subprocess
import sys
from typing import Any

CREATE_NO_WINDOW = 0x08000000
STARTF_USESHOWWINDOW = 0x00000001
SW_HIDE = 0
_PATCH_MARKER = "_cortexflow_windowless_popen"


def configure_windowless_subprocesses() -> bool:
    """Configura ``subprocess.Popen`` uma única vez no Windows.

    A configuração global é necessária porque Whisper e pytesseract criam seus
    próprios subprocessos. Argumentos explícitos do chamador, como ``stdin=PIPE``,
    continuam preservados.

    Retorna ``True`` quando o patch é aplicado e ``False`` fora do Windows ou
    quando ele já estava ativo.
    """
    if sys.platform != "win32" or getattr(subprocess.Popen, _PATCH_MARKER, False):
        return False

    original_popen = subprocess.Popen

    class WindowlessPopen(original_popen):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            kwargs["creationflags"] = kwargs.get("creationflags", 0) | CREATE_NO_WINDOW

            if kwargs.get("startupinfo") is None:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = SW_HIDE
                kwargs["startupinfo"] = startupinfo

            if getattr(sys, "frozen", False) and "stdin" not in kwargs:
                kwargs["stdin"] = subprocess.DEVNULL

            super().__init__(*args, **kwargs)

    setattr(WindowlessPopen, _PATCH_MARKER, True)
    subprocess.Popen = WindowlessPopen  # type: ignore[misc, assignment]
    return True
