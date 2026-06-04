# Debitos Tecnicos do CortexFlow

Data da analise: 2026-06-03

## Problemas Encontrados

| Area | Problema | Impacto |
|---|---|---|
| Ambiente | Workspace observado com Python 3.14.4, enquanto README declara Python 3.10+. | Risco alto para Whisper/Torch/PyInstaller, que tendem a ser mais sensiveis a versoes novas. |
| Documentacao | README referencia `CHANGELOG.md`, `instalar_dependencias.bat` e `app_transcricao.py`, mas esses arquivos nao aparecem na raiz. | Usuario pode seguir instrucoes quebradas. |
| Encoding | Saidas lidas mostram caracteres PT-BR corrompidos em varios arquivos/documentos. | Dificulta leitura, suporte e apresentacao profissional. |
| Runtime no repo | `data/` possui cache, historico, fila e logs locais. | Risco de versionar dados de usuario ou poluir diffs. |
| Artefatos gerados | `__pycache__` aparece dentro de `src/` e `tests/`. | Ruido de workspace e risco de commits acidentais. |
| Build | PyInstaller depende de muitos hidden imports e binarios externos. | Build fragil, dificil de reproduzir sem checklist automatizado. |
| UI | Paineis legados permanecem no codigo e alguns componentes nao sao usados na janela principal. | Aumenta manutencao e confusao sobre o que esta ativo. |
| Testes | Cobertura automatizada pequena frente ao tamanho do pipeline. | Risco de regressao em fila, cache, exportacao, build e UI. |

## Riscos de Manutencao

1. `JobProcessor` concentra muitas responsabilidades: cache, extracao, transcricao, exportacao, biblioteca, grafo, datasets e historico.
2. `SettingsService` tambem concentra configuracao, paths, historico, feature flags e migracao.
3. UI e worker thread exigem disciplina constante de callbacks thread-safe.
4. O pipeline avancado tem muitos modulos acoplados por imports tardios e singletons.
5. O build depende de estado local (`bin/`, versao do Python, dependencias instaladas, PyInstaller).

## Duplicacoes e Sobreposicoes

| Tema | Observacao |
|---|---|
| Resultado na UI | `result_window.py` e `result_panel.py` convivem, mas o painel embutido e legado. |
| Conhecimento | `src/knowledge/`, `src/knowledge_graph/`, `src/library/`, `src/semantic/` e `src/datasets/` se cruzam em responsabilidades. |
| Documentacao de build | `agent.md`, `README.md`, `bin/README.md` e scripts descrevem partes do build com niveis diferentes de atualizacao. |
| Caminhos de dados | Varios modulos importam `DATA_DIR` ou resolvem arquivos diretamente em `data/`. |

## Arquivos Suspeitos de Estarem Sem Uso ou de Uso Baixo

Nao remover nesta etapa. Apenas revisar futuramente:

- `src/ui/result_panel.py`: marcado como arquivado funcionalmente em `docs/UI_CLEANUP_REPORT.md`.
- `src/ui/legacy_ui/*.py`: nao montados pela janela principal atual.
- `src/ui/document_detail_panel.py`: usado apenas por painel legado.
- `src/ui/components/knowledge_widgets.py`: ligado ao workspace legado.
- `src/utils/create_icon.py`: utilitario pontual para asset, nao fluxo principal.
- `src/**/__pycache__/*`: artefatos gerados.
- `tests/**/__pycache__/*`: artefatos gerados.

## Riscos Tecnicos

| Risco | Severidade | Motivo |
|---|---|---|
| Build com Python 3.14 | Alta | Pode quebrar dependencias nativas e empacotamento de Torch/Whisper. |
| Transcricao dependente de FFmpeg local/PATH | Alta | Sem FFmpeg correto o Whisper falha em audio/video. |
| Tesseract ausente no `bin/` | Media | OCR de imagens depende de instalacao externa ou copia manual. |
| Estado local versionavel | Media | `data/` contem conteudo de usuario/cache e pode entrar em commits sem cuidado. |
| Falta de CI | Media | Regressao pode passar sem testes automatizados em PR/local. |
| UI sem testes E2E | Media | Bugs de callback, modal e drag-and-drop exigem teste manual. |
| Arquivos com encoding inconsistente | Media | Pode afetar documentacao, strings e experiencia em PT-BR. |

## Riscos de Seguranca

1. `data/` pode conter nomes de arquivos, caminhos locais, historico de transcricoes e possivel conteudo sensivel.
2. `data/logs/app.log` pode registrar paths e detalhes tecnicos de erros.
3. `bin/ffmpeg.exe` e `bin/ffprobe.exe` sao binarios grandes e devem ter origem/verificacao clara.
4. Build desktop pode acionar antivirus por empacotar Python, Torch e binarios externos.
5. OCR/Whisper processam arquivos locais do usuario; mensagens de erro e logs nao devem expor conteudo sensivel desnecessariamente.

## Pontos de Melhoria na Interface

- Trocar textos com simbolos corrompidos por textos consistentes em PT-BR.
- Melhorar feedback quando Whisper, FFmpeg, modelo ou Tesseract nao estao disponiveis.
- Adicionar tela/painel de diagnostico local: Python, FFmpeg, Tesseract, modelo Whisper, pasta de dados.
- Rever `Ctrl+E`, pois o relatorio de UX indica dependencia da janela de resultado.
- Dar visibilidade clara a cache hit/miss, saida final e erro tecnico resumido.
- Definir destino futuro dos paineis `legacy_ui`.

## Pontos de Melhoria no Motor de Transcricao

- Validar FFmpeg antes de iniciar fila e antes de carregar modelo pesado.
- Padronizar diagnostico de erro de Whisper/FFmpeg com logs acionaveis.
- Testar caminho de transcricao com audio curto fixture/mockado.
- Permitir fallback configuravel de modelo e idioma.
- Medir tempo de carregamento do modelo separadamente do tempo de transcricao.
- Avaliar isolamento de subprocessos sem interferir em pipes usados por FFmpeg.

## Melhorias nos Testes

- Testes de `QueueManager` com fila, cancelamento e recovery.
- Testes de `PersistentQueue` com JSON corrompido, processing reset e truncamento.
- Testes de `CacheEngine` e `cache_registry`.
- Testes de `ExportService` para raw, clean, AI-ready, NotebookLM e JSON.
- Testes de `job_errors` para FFmpeg ausente, arquivo ausente, permissao e path longo.
- Testes de `ExtractionService` com TXT, PDF/DOCX/XLSX pequenos e OCR mockado.
- Teste de build smoke sem empacotar tudo: validar imports e hidden imports.

## Melhorias no Build/Empacotamento

- Definir oficialmente Python 3.10/3.11/3.12 para build.
- Criar checklist unico de release em `docs/`.
- Verificar existencia de `ffmpeg.exe`, `ffprobe.exe`, `tesseract.exe` e `tessdata/`.
- Documentar como lidar com antivirus/SmartScreen.
- Separar dados do usuario do pacote distribuivel.
- Validar `dist/CortexFlow/CortexFlow.exe` com teste manual minimo antes de release.

## Pontos que Precisam de Revisao Humana

1. Confirmar se `data/` deve permanecer no repo ou ser tratado apenas como runtime local.
2. Confirmar se `legacy_ui` deve voltar no futuro ou ser arquivado fora de `src/`.
3. Confirmar versao alvo de Python para desenvolvimento e build.
4. Confirmar origem e politica de atualizacao dos binarios FFmpeg.
5. Confirmar se README deve apontar para repo `nilknarfsam/cortexflow` e nao `seu-usuario/transcritor-universal`.
