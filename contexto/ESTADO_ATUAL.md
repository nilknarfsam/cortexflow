# Estado atual

Última revisão: 2026-08-12

## Produto

CortexFlow está em processo de migração de arquitetura para **C# .NET 9 com WinUI 3**. A base legada em Python 3.12 (CustomTkinter) foi preservada sob `legacy_python/` com todos os 63 testes unitários mantidos e operacionais.

O repositório principal agora abriga a solução `CortexFlow.sln` (.NET 9):
- `src/CortexFlow.Core`: Modelos de domínio (`QueueItem`, `TranscriptionResult`, `JobSettings`), abstrações (`ITranscriptionService`, `ICacheService`, `IQueueManager`, `IExportService`), serviços de cache SHA-256 e exportador.
- `src/CortexFlow.Infrastructure`: Implementações de mídia e integração de sistema.
- `tests/CortexFlow.Core.Tests`: Testes automatizados em xUnit (4 testes xUnit aprovados).
- `legacy_python/`: Protótipo original em Python 3.12 preservado para referência e migração gradual.

## Fotografia técnica

| Indicador | Estado em 2026-08-12 |
|---|---|
| Runtime Alvo | .NET 9 SDK (9.0.305) + Windows 10/11 WinUI 3 / WPF Fluent |
| Solução C# | `CortexFlow.sln` com `CortexFlow.Core`, `CortexFlow.Infrastructure`, `CortexFlow.UI` e `CortexFlow.Core.Tests` |
| Formatação de Transcrição | Novo modo **`Time Blocks (Blocos de Tempo de 30s)`** (`### ⏱️ [MM:SS - MM:SS]`) + parágrafos formatados legíveis no modo `Clean` |
| Manual do Usuário (XAML) | **`HelpWindow.xaml`** (F1) com 5 abas intuitivas: Início Rápido, Predefinições, Modelos Whisper, Atalhos de Teclado, Privacidade & 5S |
| Diretrizes de Qualidade | Criado o documento `docs/DESENVOLVIMENTO_5S_KPIS_SEGURANCA.md` alinhado à filosofia 5S, KPIs e segurança de dados |
| Estilo Dark Mode dos Menus | Estilização XAML de `MenuItem` (`Background="#1E293B" Foreground="#F8FAFC"` e highlight `#0EA5E9`), 100% legível |
| Interface Gráfica Profissional | `MainWindow.xaml` no **estilo Conversor de Mídia Studio (85% DataGrid)** com Menu Bar nativa, Toolbar de atalhos, StatusBar dinâmica e rodapé de presets |
| Atalho de Execução | `run_app.bat` e `setup_and_run.bat` (ASCII puro) com rebuild automático a cada execução |
| Tradução Automática | Suporte nativo ao `.WithTranslate()` do `Whisper.net` via checkbox **`TranslateCheck`** |
| GitHub Actions CI/CD | Pipeline `.github/workflows/quality.yml` atualizado para **100% .NET 9 (Restore, Build Release, xUnit)** |
| Pré-processador de Mídia | **`AudioPreProcessor` (FFmpeg)** converte automaticamente qualquer vídeo/áudio (`.mp4`, `.mp3`, `.mkv`) para WAV 16kHz mono |
| Opções de Exportação | Salvar na pasta de origem ou pasta customizada nos formatos **.md, .txt, .json e .pdf** |
| Testes C# | **16 testes `xUnit` aprovados** em `CortexFlow.Core.Tests` (100% OK em 80ms) |














## Pontos fortes

- Processamento local e orientado à privacidade.
- Fila persistente com recuperação e cache.
- Separação razoável entre UI, núcleo, extração, exportação e recursos avançados.
- Build Windows documentado e preparado para FFmpeg local.
- Testes atuais rápidos e estáveis.

## Limitações e riscos confirmados

1. A cobertura de testes é pequena diante do tamanho do núcleo.
2. `JobProcessor`, `SettingsService` e componentes da UI concentram muitas
   responsabilidades.
3. O artefato one-directory ainda é grande devido a PyTorch, Whisper e FFmpeg.
4. Avisos opcionais do PyInstaller precisam ser reavaliados em atualizações de
   PyTorch, Numba ou PyInstaller.
5. O patch global de `subprocess.Popen` continua necessário para chamadas internas
   de Whisper e pytesseract, agora isolado e coberto por testes.
6. Código de UI legado permanece dentro do pacote principal.

## Proteções já implantadas

- Gravação JSON atômica compartilhada por fila, configurações, histórico e
  registro de cache.
- Recuperação da fila tolerante a progresso inválido, não finito ou fora do
  intervalo de 0 a 1.
- Metadados de dataset preservados ao salvar e restaurar a fila.
- Testes garantem que uma falha de serialização preserve o arquivo JSON anterior.
- Persistência de settings, histórico e registro de cache verificada em diretórios
  temporários.
- Exportação raw em TXT, Markdown e JSON e classificação dos principais erros
  possuem testes de regressão.
- Cache coberto para miss, partial, hit, mudança de configuração, corrupção,
  chunks e limpeza.
- Fila coberta para adição, arquivo ausente/inválido, seleção, remoção, início,
  conclusão e recuperação de contadores corrompidos.
- Processamento de job coberto para documento novo, cache, cancelamento e erro,
  usando serviços falsos sem carregar Whisper.
- Cobertura do núcleo (`core`, `cache`, `models`) medida em 62%, com piso de CI
  em 55%.
- Diagnóstico seguro disponível nas configurações para FFmpeg, FFprobe,
  Tesseract, Whisper, PyTorch, modelo base e pasta de dados.
- Subprocessos Windows configurados de forma idempotente, preservando `stdin`,
  `startupinfo` e flags fornecidas pelo chamador.
- Build valida executável, FFmpeg e FFprobe e executa smoke test sem abrir a GUI.

## Documentação histórica

Relatórios detalhados continuam disponíveis em `docs/`. Eles são evidência
histórica e podem estar desatualizados; valide conclusões contra código e testes.
O antigo `agent.md` também deve ser tratado como legado até sua migração completa.
