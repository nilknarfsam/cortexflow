from __future__ import annotations

import subprocess
import unittest
from contextlib import contextmanager
from collections.abc import Iterator
from unittest.mock import patch

from src.core.windows_subprocess import (
    CREATE_NO_WINDOW,
    STARTF_USESHOWWINDOW,
    configure_windowless_subprocesses,
)


class _FakeStartupInfo:
    def __init__(self) -> None:
        self.dwFlags = 0
        self.wShowWindow = None


class _FakePopen:
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.calls.append((args, kwargs))


class TestWindowlessSubprocess(unittest.TestCase):
    def setUp(self) -> None:
        _FakePopen.calls = []

    @contextmanager
    def _configured(self, *, frozen: bool = False) -> Iterator[type[subprocess.Popen]]:
        frozen_patch = patch("src.core.windows_subprocess.sys.frozen", frozen, create=True)
        with (
            patch("src.core.windows_subprocess.sys.platform", "win32"),
            patch("src.core.windows_subprocess.subprocess.Popen", _FakePopen),
            patch("src.core.windows_subprocess.subprocess.STARTUPINFO", _FakeStartupInfo),
            frozen_patch,
        ):
            self.assertTrue(configure_windowless_subprocesses())
            yield subprocess.Popen

    def test_patch_adds_windowless_flags_and_startup_info(self) -> None:
        with self._configured() as patched_popen:
            patched_popen(["ffmpeg", "-version"], creationflags=4)

        _, kwargs = _FakePopen.calls[-1]
        self.assertEqual(kwargs["creationflags"], 4 | CREATE_NO_WINDOW)
        startupinfo = kwargs["startupinfo"]
        self.assertIsInstance(startupinfo, _FakeStartupInfo)
        self.assertEqual(startupinfo.dwFlags & STARTF_USESHOWWINDOW, STARTF_USESHOWWINDOW)

    def test_explicit_stdin_and_startup_info_are_preserved(self) -> None:
        supplied_startupinfo = _FakeStartupInfo()

        with self._configured(frozen=True) as patched_popen:
            patched_popen(
                ["tesseract", "--version"],
                stdin=subprocess.PIPE,
                startupinfo=supplied_startupinfo,
            )

        _, kwargs = _FakePopen.calls[-1]
        self.assertIs(kwargs["stdin"], subprocess.PIPE)
        self.assertIs(kwargs["startupinfo"], supplied_startupinfo)

    def test_frozen_process_without_stdin_uses_devnull(self) -> None:
        with self._configured(frozen=True) as patched_popen:
            patched_popen(["ffprobe", "-version"])

        _, kwargs = _FakePopen.calls[-1]
        self.assertIs(kwargs["stdin"], subprocess.DEVNULL)

    def test_configuration_is_idempotent(self) -> None:
        with (
            patch("src.core.windows_subprocess.sys.platform", "win32"),
            patch("src.core.windows_subprocess.subprocess.Popen", _FakePopen),
            patch("src.core.windows_subprocess.subprocess.STARTUPINFO", _FakeStartupInfo),
        ):
            self.assertTrue(configure_windowless_subprocesses())
            first_popen = subprocess.Popen
            self.assertFalse(configure_windowless_subprocesses())
            self.assertIs(subprocess.Popen, first_popen)

    def test_non_windows_does_not_patch(self) -> None:
        with (
            patch("src.core.windows_subprocess.sys.platform", "linux"),
            patch("src.core.windows_subprocess.subprocess.Popen", _FakePopen),
        ):
            self.assertFalse(configure_windowless_subprocesses())
            self.assertIs(subprocess.Popen, _FakePopen)
