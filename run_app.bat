@echo off
title CortexFlow 4.0 - Executador Desktop

echo ========================================================
echo   CortexFlow 4.0 (.NET 9 / WinUI 3 Engine)
echo ========================================================
echo.

echo Compilando e iniciando o CortexFlow...
dotnet run --project src\CortexFlow.UI\CortexFlow.UI.csproj

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha na execucao do projeto.
    pause
    exit /b %ERRORLEVEL%
)
