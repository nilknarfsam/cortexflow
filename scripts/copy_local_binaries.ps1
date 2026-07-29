# Copia FFmpeg (e Tesseract, se instalado) para bin/ antes do build standalone.
param(
    [string]$Destination = ""
)

$ErrorActionPreference = "Stop"
$dest = if ($Destination) {
    $Destination
} else {
    Join-Path (Split-Path $PSScriptRoot -Parent) "bin"
}
New-Item -ItemType Directory -Force -Path $dest | Out-Null

function Copy-IfExists($path, $name) {
    if (Test-Path -LiteralPath $path) {
        Copy-Item -LiteralPath $path -Destination (Join-Path $dest $name) -Force
        Write-Host "OK: $name <- $path"
        return $true
    }
    return $false
}

$ffmpegCopied = $false
$ffprobeCopied = $false
$ffmpegSrc = Get-Command ffmpeg -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
$ffprobeSrc = Get-Command ffprobe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
if ($ffmpegSrc) {
    $ffmpegCopied = Copy-IfExists $ffmpegSrc "ffmpeg.exe"
}
if ($ffprobeSrc) {
    $ffprobeCopied = Copy-IfExists $ffprobeSrc "ffprobe.exe"
}

if (-not ($ffmpegCopied -and $ffprobeCopied)) {
    $wingetPkg = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "FFmpeg" } | Select-Object -First 1
    if ($wingetPkg) {
        if (-not $ffmpegCopied) {
            $candidate = Get-ChildItem $wingetPkg.FullName -Recurse -File -Filter "ffmpeg.exe" -ErrorAction SilentlyContinue |
                Select-Object -First 1
            if ($candidate) {
                $ffmpegCopied = Copy-IfExists $candidate.FullName "ffmpeg.exe"
            }
        }
        if (-not $ffprobeCopied) {
            $candidate = Get-ChildItem $wingetPkg.FullName -Recurse -File -Filter "ffprobe.exe" -ErrorAction SilentlyContinue |
                Select-Object -First 1
            if ($candidate) {
                $ffprobeCopied = Copy-IfExists $candidate.FullName "ffprobe.exe"
            }
        }
    }
}

$ffmpegCopied = Test-Path -LiteralPath (Join-Path $dest "ffmpeg.exe")
$ffprobeCopied = Test-Path -LiteralPath (Join-Path $dest "ffprobe.exe")
if (-not ($ffmpegCopied -and $ffprobeCopied)) {
    Write-Warning "FFmpeg/FFprobe nao foram encontrados para copia em bin/."
}

$tesseractPaths = @(
    "${env:ProgramFiles}\Tesseract-OCR\tesseract.exe",
    "${env:ProgramFiles(x86)}\Tesseract-OCR\tesseract.exe"
)
foreach ($tp in $tesseractPaths) {
    if (Copy-IfExists $tp "tesseract.exe") {
        $tessDir = Join-Path (Split-Path $tp -Parent) "tessdata"
        if (Test-Path $tessDir) {
            Copy-Item -Path $tessDir -Destination (Join-Path $dest "tessdata") -Recurse -Force
            Write-Host "OK: tessdata/ <- $tessDir"
        }
        break
    }
}

Write-Host "`nConteúdo de bin/:"
Get-ChildItem $dest | Format-Table Name, Length -AutoSize
