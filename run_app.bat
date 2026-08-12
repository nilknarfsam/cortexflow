@echo off
chcp 65001 > nul
title CortexFlow 4.0 - Executador Desktop

echo ========================================================
echo   ⚡ Iniciando CortexFlow 4.0 (.NET 9 / WinUI 3)
echo ========================================================
echo.

set EXE_PATH=src\CortexFlow.UI\bin\Debug\net9.0-windows\CortexFlow.UI.exe

if not exist "%EXE_PATH%" (
    echo Compilando a solução .NET 9 pela primeira vez...
    dotnet build
    echo.
)

if exist "%EXE_PATH%" (
    echo Abrindo o CortexFlow...
    start "" "%EXE_PATH%"
) else (
    echo [ERRO] Não foi possível compilar ou encontrar o executável.
    echo Certifique-se de que o .NET 9 SDK está instalado.
    pause
)
