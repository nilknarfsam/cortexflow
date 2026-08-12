@echo off
title CortexFlow 4.0 - Executador Desktop

echo ========================================================
echo   CortexFlow 4.0 (.NET 9 / WinUI 3)
echo ========================================================
echo.

set EXE_PATH=src\CortexFlow.UI\bin\Debug\net9.0-windows\CortexFlow.UI.exe

if not exist "%EXE_PATH%" (
    echo Compilando a solucao .NET 9 pela primeira vez...
    dotnet build
    echo.
)

if exist "%EXE_PATH%" (
    echo Abrindo o CortexFlow...
    start "" "%EXE_PATH%"
) else (
    echo [ERRO] Nao foi possivel compilar ou encontrar o executavel.
    echo Certifique-se de que o .NET 9 SDK esta instalado.
    pause
)
