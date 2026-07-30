# Binários locais

Esta pasta é priorizada no `PATH` pelo bootstrap de `app.py` e empacotada pelo
`app_transcricao.spec`.

## Conteúdo esperado

| Arquivo | Função |
|---------|--------|
| `ffmpeg.exe` | Transcrição de áudio/vídeo (Whisper) |
| `ffprobe.exe` | Metadados de mídia (FFmpeg) |
| `tesseract.exe` | OCR de imagens (opcional) |
| `tessdata/` | Idiomas Tesseract (opcional) |

## Origem validada

| Componente | Versão | Distribuição |
|---|---|---|
| FFmpeg e FFprobe | 8.1.1 | Gyan FFmpeg Essentials via WinGet |

Instalação:

```powershell
winget install --id Gyan.FFmpeg -e
```

O script resolve tanto comandos no `PATH` quanto a instalação gerenciada pelo
WinGet e valida os dois executáveis:

```powershell
.\scripts\copy_local_binaries.ps1
```

Os arquivos `.exe` não são versionados no Git. Eles devem ser copiados novamente
antes de cada build de distribuição.
