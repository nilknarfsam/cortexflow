"""Testes dos códigos estáveis e mensagens de erro de processamento."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from urllib.error import URLError

from src.core.job_errors import classify_job_error, format_traceback


class TestClassifyJobError(unittest.TestCase):
    def assert_code(self, exc: BaseException, expected: str, path: str = "") -> None:
        info = classify_job_error(exc, path)
        self.assertEqual(info.error_code, expected)
        self.assertTrue(info.user_message)
        self.assertIn(type(exc).__name__, info.technical_detail)

    def test_missing_source_file(self) -> None:
        self.assert_code(
            FileNotFoundError("não encontrado"),
            "FILE_NOT_FOUND",
            "arquivo-ausente.mp3",
        )

    def test_missing_ffmpeg_when_source_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "audio.mp3"
            source.write_bytes(b"audio")
            self.assert_code(
                FileNotFoundError("ffmpeg"),
                "FFMPEG_NOT_FOUND",
                str(source),
            )

    def test_specific_runtime_errors(self) -> None:
        cases = (
            (PermissionError("negado"), "PERMISSION_DENIED"),
            (MemoryError(), "OUT_OF_MEMORY"),
            (ImportError("pacote"), "MISSING_DEPENDENCY"),
            (RuntimeError("Whisper não instalado"), "WHISPER_UNAVAILABLE"),
            (URLError("SSL indisponível"), "WHISPER_DOWNLOAD_FAILED"),
            (OSError("file name too long"), "PATH_TOO_LONG"),
            (OSError("falha genérica"), "OS_ERROR"),
            (ValueError("formato inválido"), "INVALID_VALUE"),
        )
        for exc, expected in cases:
            with self.subTest(expected=expected):
                self.assert_code(exc, expected, "entrada.mp3")

    def test_unknown_error_message_is_limited(self) -> None:
        info = classify_job_error(Exception("x" * 500), "entrada.mp3")
        self.assertEqual(info.error_code, "PROCESSING_ERROR")
        self.assertLessEqual(len(info.user_message), 230)

    def test_format_traceback_contains_exception_context(self) -> None:
        try:
            raise ValueError("teste")
        except ValueError as exc:
            formatted = format_traceback(exc)
        self.assertIn("ValueError: teste", formatted)
        self.assertIn("test_format_traceback", formatted)


if __name__ == "__main__":
    unittest.main()
