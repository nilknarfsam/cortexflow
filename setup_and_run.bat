@echo off
title CortexFlow 4.0 - Executador 1-Clique

echo =======================================================================
echo   CortexFlow 4.0 (.NET 9 / WinUI 3 Engine)
echo   Instalacao de Dependencias e Execucao Direta pelo Terminal
echo =======================================================================
echo.

echo [1/4] Verificando instalacao do .NET 9 SDK...
dotnet --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO CRITICO] .NET 9 SDK nao foi encontrado no seu computador!
    echo Para executar o CortexFlow, voce precisa instalar o .NET 9 SDK.
    echo.
    echo Instale pelo terminal executando o comando:
    echo   winget install Microsoft.DotNet.SDK.9
    echo.
    pause
    exit /b 1
)
echo [OK] .NET SDK detectado!

echo.
echo [2/4] Verificando presenca do FFmpeg...
ffmpeg -version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] FFmpeg nao foi encontrado no PATH global do Windows.
    echo O CortexFlow usara o ffmpeg.exe local ou converter via fallback.
) else (
    echo [OK] FFmpeg detectado no PATH do sistema!
)

echo.
echo [3/4] Restaurando pacotes e dependencias NuGet do .NET 9...
dotnet restore CortexFlow.sln --nologo
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao restaurar pacotes NuGet.
    pause
    exit /b 1
)
echo [OK] Dependencias NuGet restauradas com sucesso!

echo.
echo [4/4] Executando suite de testes automatizados (xUnit)...
dotnet test CortexFlow.sln --nologo --verbosity quiet
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Alguns testes falharam, mas tentaremos iniciar a aplicacao...
) else (
    echo [OK] Todos os testes automatizados foram APROVADOS!
)

echo.
echo =======================================================================
echo   Iniciando o CortexFlow v4.0 diretamente pelo terminal...
echo =======================================================================
echo.

dotnet run --project src\CortexFlow.UI\CortexFlow.UI.csproj --nologo

pause