param(
    [string]$PythonPath = ""
)

$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
$venvPython = if ($PythonPath) {
    $PythonPath
} elseif ($env:CORTEXFLOW_PYTHON) {
    $env:CORTEXFLOW_PYTHON
} else {
    Join-Path $root ".venv\Scripts\python.exe"
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Comando falhou ($LASTEXITCODE): $FilePath $($Arguments -join ' ')"
    }
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Ambiente virtual nao encontrado em $venvPython. Crie com Python 3.12 e instale as dependencias."
}

Invoke-Checked $venvPython -c "import sys; print(sys.version); assert sys.version_info[:2] == (3, 12), 'Use Python 3.12 para o build oficial do CortexFlow.'"
Invoke-Checked $venvPython -c "import whisper, torch, customtkinter, tkinterdnd2, PIL, pdfplumber, docx, openpyxl, pytesseract; print('Dependencias OK')"

& (Join-Path $PSScriptRoot "copy_local_binaries.ps1")

$ffmpeg = Join-Path $root "bin\ffmpeg.exe"
if (-not (Test-Path -LiteralPath $ffmpeg)) {
    throw "ffmpeg.exe nao encontrado em bin\. Copie o FFmpeg antes do build."
}

Push-Location $root
try {
    Invoke-Checked $venvPython -m PyInstaller --clean --noconfirm app_transcricao.spec
}
finally {
    Pop-Location
}

Write-Host ""
$distDir = Join-Path $root "dist\CortexFlow"
$executable = Join-Path $distDir "CortexFlow.exe"
$ffmpegDist = Join-Path $distDir "_internal\bin\ffmpeg.exe"
$ffprobeDist = Join-Path $distDir "_internal\bin\ffprobe.exe"

foreach ($requiredFile in @($executable, $ffmpegDist, $ffprobeDist)) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "Build incompleto: arquivo obrigatorio ausente em $requiredFile"
    }
}

$smokeProcess = Start-Process `
    -FilePath $executable `
    -ArgumentList "--smoke-test" `
    -WorkingDirectory $distDir `
    -WindowStyle Hidden `
    -Wait `
    -PassThru
if ($smokeProcess.ExitCode -ne 0) {
    throw "Smoke test do executavel falhou com codigo $($smokeProcess.ExitCode)."
}

Write-Host "Smoke test do executavel: OK"
Write-Host "Build concluido em: $executable"
