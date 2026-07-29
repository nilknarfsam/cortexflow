# Estado atual

Última revisão: 2026-07-28

## Produto

CortexFlow 3.0.4 é uma aplicação desktop local em Python para transcrever áudio
e vídeo e extrair conteúdo de documentos e imagens. A interface usa
CustomTkinter, e o processamento de mídia usa OpenAI Whisper e FFmpeg.

O fluxo principal está concentrado em:

- `app.py`: preparação do runtime e entrada da aplicação.
- `src/ui/main_window.py`: janela principal.
- `src/core/queue_manager.py`: fila, worker, persistência e callbacks.
- `src/core/job_processor.py`: pipeline de processamento de cada item.
- `src/core/transcription_service.py`: integração com Whisper.
- `src/core/extraction_service.py`: documentos e OCR.
- `src/core/export_service.py` e `src/ai_ready/`: formatos de saída.

## Fotografia técnica

| Indicador | Estado em 2026-07-28 |
|---|---|
| Branch | `main`, alinhada com `origin/main` no momento da revisão |
| Código Python | 134 arquivos e aproximadamente 14.600 linhas em `src/` |
| Testes | 57 testes `unittest`, todos aprovados com Python 3.12 |
| Compilação | `compileall` aprovado |
| Tooling | `pyproject.toml`, Ruff, coverage e GitHub Actions configurados |
| Dependências | Dependências diretas fixadas nas versões validadas; Python 3.12 como alvo oficial |
| Build | PyInstaller em modo one-directory |
| FFmpeg local | `ffmpeg.exe` e `ffprobe.exe` 8.1.1 disponíveis em `bin/` e ignorados pelo Git |
| Execução da GUI | Validada em 2026-07-28 com Python 3.12; janela `CortexFlow 3.0.4` abriu e permaneceu responsiva |
| Dados locais | JSON, cache e logs sob `data/`; arquivos de runtime principais ignorados |
| UI legada | Seis módulos mantidos em `src/ui/legacy_ui/` |

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
3. Não há validação automática em pull requests.
4. O build pode variar conforme versões não fixadas de Python e dependências.
5. `app.py` substitui globalmente `subprocess.Popen` no Windows.
6. O build one-directory ainda não possui smoke test automatizado do executável.
7. Código de UI legado permanece dentro do pacote principal.

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
- Cobertura do núcleo (`core`, `cache`, `models`) medida em 61%, com piso de CI
  em 55%.
- Diagnóstico seguro disponível nas configurações para FFmpeg, FFprobe,
  Tesseract, Whisper, PyTorch, modelo base e pasta de dados.

## Documentação histórica

Relatórios detalhados continuam disponíveis em `docs/`. Eles são evidência
histórica e podem estar desatualizados; valide conclusões contra código e testes.
O antigo `agent.md` também deve ser tratado como legado até sua migração completa.
