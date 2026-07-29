"""Testes do diagnóstico local sem executar binários reais."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.core.environment_diagnostics import (
    ComponentDiagnostic,
    EnvironmentDiagnosticReport,
    _can_write_data_dir,
    _first_version_line,
    _whisper_model_diagnostic,
    collect_environment_diagnostics,
)


class TestEnvironmentDiagnostics(unittest.TestCase):
    def test_binary_version_is_collected_without_exposing_path(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["ffmpeg", "-version"],
            returncode=0,
            stdout="ffmpeg version 8.1.1-essentials_build Copyright\n",
            stderr="",
        )
        with (
            patch(
                "src.core.environment_diagnostics.shutil.which",
                return_value=r"C:\Ferramentas\ffmpeg.exe",
            ),
            patch(
                "src.core.environment_diagnostics.subprocess.run",
                return_value=completed,
            ),
        ):
            result = _first_version_line("ffmpeg")

        self.assertTrue(result.available)
        self.assertEqual(result.version, "8.1.1-essentials_build")
        self.assertNotIn("Ferramentas", result.detail)

    def test_missing_tesseract_is_marked_optional(self) -> None:
        with patch(
            "src.core.environment_diagnostics.shutil.which",
            return_value=None,
        ):
            result = _first_version_line("tesseract")

        self.assertFalse(result.available)
        self.assertIn("opcional", result.detail)

    def test_binary_timeout_is_reported_safely(self) -> None:
        with (
            patch(
                "src.core.environment_diagnostics.shutil.which",
                return_value="ffprobe",
            ),
            patch(
                "src.core.environment_diagnostics.subprocess.run",
                side_effect=subprocess.TimeoutExpired("ffprobe", 5),
            ),
        ):
            result = _first_version_line("ffprobe")

        self.assertFalse(result.available)
        self.assertIn("TimeoutExpired", result.detail)

    def test_data_directory_write_check_cleans_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data"
            self.assertTrue(_can_write_data_dir(data_dir))
            self.assertEqual(list(data_dir.iterdir()), [])

    def test_whisper_model_reports_local_or_first_download(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir)
            missing = _whisper_model_diagnostic("base", cache_dir=cache_dir)
            self.assertFalse(missing.available)
            self.assertIn("primeiro uso", missing.detail)

            (cache_dir / "base.pt").write_bytes(b"modelo")
            available = _whisper_model_diagnostic("base", cache_dir=cache_dir)
            self.assertTrue(available.available)
            self.assertIn("localmente", available.detail)

    def test_safe_report_does_not_include_local_paths(self) -> None:
        report = EnvironmentDiagnosticReport(
            generated_at="2026-07-28T23:59:00+00:00",
            python_version="3.12.0",
            operating_system="Windows 11 (AMD64)",
            data_writable=True,
            components=(
                ComponentDiagnostic("FFmpeg", True, "8.1.1"),
                ComponentDiagnostic("FFprobe", True, "8.1.1"),
                ComponentDiagnostic("Tesseract", False, detail="opcional"),
                ComponentDiagnostic("Whisper", True, "20250625"),
            ),
        )

        text = report.to_safe_text()

        self.assertTrue(report.healthy)
        self.assertIn("Estado geral: OK", text)
        self.assertNotIn("C:\\", text)

    def test_collection_uses_requested_data_directory(self) -> None:
        components = (
            ComponentDiagnostic("FFmpeg", True),
            ComponentDiagnostic("FFprobe", True),
            ComponentDiagnostic("Tesseract", False),
            ComponentDiagnostic("Whisper", True),
            ComponentDiagnostic("PyTorch", True),
            ComponentDiagnostic("Modelo Whisper (base)", False),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                patch(
                    "src.core.environment_diagnostics._first_version_line",
                    side_effect=components[:3],
                ),
                patch(
                    "src.core.environment_diagnostics._package_diagnostic",
                    side_effect=components[3:5],
                ),
                patch(
                    "src.core.environment_diagnostics._whisper_model_diagnostic",
                    return_value=components[5],
                ),
            ):
                report = collect_environment_diagnostics(
                    data_dir=Path(temp_dir) / "data"
                )

        self.assertTrue(report.healthy)
        self.assertEqual(len(report.components), 6)


if __name__ == "__main__":
    unittest.main()
