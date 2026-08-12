@echo off
title CortexFlow 4.0 - Executador Desktop

echo ========================================================
echo   CortexFlow 4.0 (.NET 9 / WinUI 3 Engine)
echo ========================================================
echo.

echo Compilando o projeto CortexFlow...
dotnet build --configuration Debug --nologo

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha na compilacao do projeto.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Abrindo o CortexFlow...
start "" "src\CortexFlow.UI\bin\Debug\net9.0-windows\CortexFlow.UI.exe"
