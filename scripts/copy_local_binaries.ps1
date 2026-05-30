# Copia FFmpeg (e Tesseract, se instalado) para bin/ antes do build standalone.
$ErrorActionPreference = "Stop"
$dest = Join-Path (Split-Path $PSScriptRoot -Parent) "bin"
New-Item -ItemType Directory -Force -Path $dest | Out-Null

function Copy-IfExists($path, $name) {
    if (Test-Path -LiteralPath $path) {
        Copy-Item -LiteralPath $path -Destination (Join-Path $dest $name) -Force
        Write-Host "OK: $name <- $path"
        return $true
    }
    return $false
}

$ffmpegSrc = Get-Command ffmpeg -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
if ($ffmpegSrc) {
    $dir = Split-Path $ffmpegSrc -Parent
    Copy-IfExists (Join-Path $dir "ffmpeg.exe") "ffmpeg.exe" | Out-Null
    Copy-IfExists (Join-Path $dir "ffprobe.exe") "ffprobe.exe" | Out-Null
} else {
    $wingetPkg = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "FFmpeg" } | Select-Object -First 1
    if ($wingetPkg) {
        $bin = Get-ChildItem $wingetPkg.FullName -Recurse -Directory -Filter "bin" -ErrorAction SilentlyContinue |
            Where-Object { Test-Path (Join-Path $_.FullName "ffmpeg.exe") } | Select-Object -First 1
        if ($bin) {
            Copy-IfExists (Join-Path $bin.FullName "ffmpeg.exe") "ffmpeg.exe" | Out-Null
            Copy-IfExists (Join-Path $bin.FullName "ffprobe.exe") "ffprobe.exe" | Out-Null
        }
    }
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
