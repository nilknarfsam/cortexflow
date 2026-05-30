# Binários locais (Standalone / Portátil)

Pasta injetada no `PATH` por `inject_local_binaries_to_path()` em `app.py` e empacotada via `app_transcricao.spec` (`datas` → `bin/`).

## Conteúdo esperado

| Arquivo | Função |
|---------|--------|
| `ffmpeg.exe` | Transcrição de áudio/vídeo (Whisper) |
| `ffprobe.exe` | Metadados de mídia (FFmpeg) |
| `tesseract.exe` | OCR de imagens (opcional) |
| `tessdata/` | Idiomas Tesseract (opcional) |

## Automação (Windows)

Origem detectada via WinGet (2026-05-30):

```
%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-essentials_build\bin\
```

Comando PowerShell para recopiar FFmpeg:

```powershell
$src = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-essentials_build\bin"
Copy-Item -LiteralPath "$src\ffmpeg.exe","$src\ffprobe.exe" -Destination "$PSScriptRoot" -Force
```

> Os `.exe` **não** são versionados no Git (ver `.gitignore`). Copie-os localmente antes do build PyInstaller.
