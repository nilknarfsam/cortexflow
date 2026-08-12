# Roadmap

Última revisão: 2026-08-12

Execução detalhada: [`PLANO_EXECUCAO.md`](PLANO_EXECUCAO.md) e `contexto/ESTADO_ATUAL.md`.

## Visão

Evoluir o CortexFlow de um protótipo Python para um produto desktop profissional de alta performance em **C# / .NET 9 (WinUI 3 / WPF Fluent)**, garantindo processamento 100% offline, tamanho de instalador reduzido (de 3GB para 200MB) e interface de conversa e transcrição de mídias de alto nível.

## Horizonte 1 — Base confiável (Concluído)

- [Concluído] Corrigir instalação, links e comandos do README.
- [Concluído] Adotar `pyproject.toml` como configuração central.
- [Concluído] Configurar lint, formatação e cobertura.
- [Concluído] Criar CI para versões de Python oficialmente suportadas.
- [Concluído] Fixar ou limitar versões de dependências.
- [Concluído] Cobrir fila, persistência, cache, exportação e classificação de erros.

## Horizonte 2 — Runtime diagnosticável (Concluído)

- [Concluído] Diagnosticar FFmpeg, FFprobe, Tesseract, Python e modelo Whisper.
- [Concluído] Exibir mensagens acionáveis e opção de copiar diagnóstico.
- [Concluído] Padronizar logs sem expor conteúdo sensível.
- [Concluído] Criar smoke test do build.

## Horizonte 3 — Nova Arquitetura C# / .NET 9 (Concluído)

- [Concluído] Reorganizar a estrutura mantendo a base legada isolada em `legacy_python/`.
- [Concluído] Criar solução C# .NET 9 (`CortexFlow.sln`) com arquitetura limpa desacoplada:
  - `CortexFlow.Core`: Abstrações, Modelos, Domínio e MVVM (`MainViewModel`).
  - `CortexFlow.Infrastructure`: `WhisperTranscriptionService` (`Whisper.net`), `AudioPreProcessor` (FFmpeg), `DocumentExtractorService` (PdfPig / OpenXml) e `WindowsOcrService`.
  - `CortexFlow.UI`: Interface WPF/WinUI 3 nativa estilo **Conversor de Mídia Profissional**.
  - `tests/CortexFlow.Core.Tests`: Suíte de testes automatizados `xUnit` (15 testes passando em 79ms).
- [Concluído] Pré-processamento FFmpeg automático para converter qualquer vídeo/áudio (`.mp4`, `.mp3`, `.mkv`) em WAV 16kHz mono, eliminando o erro *Invalid wave file RIFF header*.
- [Concluído] Suporte a exportação multi-formato (`.md`, `.txt`, `.json`, `.pdf`), seletor de pasta customizada e salvamento na pasta do arquivo de origem.
- [Concluído] Modal de Configurações Avançadas e Diagnósticos do Ambiente (`SettingsWindow.xaml`).
- [Concluído] Janela Visualizadora de Resultados com abas de transcrição e linha do tempo de timestamps (`ResultWindow.xaml`).
- [Concluído] GitHub Actions CI/CD automatizado em .NET 9 (`.github/workflows/quality.yml`).

## Horizonte 4 — Próximos Recursos Avançados (Em Planejamento)

- [ ] Suporte a múltiplos idiomas na detecção automática e tradução nativa do Whisper.
- [ ] Exportação de relatórios estendidos com mapas mentais / gráficos de conhecimento visual.
- [ ] Empacotamento para distribuição Windows (Instalador MSIX / Portable zip).
