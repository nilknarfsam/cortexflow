# Analise Geral do CortexFlow pelo Codex

Data da analise: 2026-06-03  
Escopo: leitura de `agent.md`, `README.md`, `src/`, `tests/`, `scripts/`, `docs/`, `data/`, `assets/` e `bin/`.  
Modo: analise documental e estrutural, sem alteracao funcional.

## Visao Geral

O CortexFlow e uma aplicacao desktop local para transformar audio, video, documentos e imagens em texto exportavel. O produto combina uma GUI em CustomTkinter, fila persistente, cache por hash, Whisper para transcricao, extratores de documentos/OCR e um pipeline opcional de enriquecimento semantico voltado a NotebookLM, estudo, biblioteca local, grafo de conhecimento e datasets.

O ponto de entrada atual e `app.py`, que prepara o ambiente Windows/PyInstaller, injeta binarios locais no `PATH` e inicializa `src.ui.main_window.run_app()`.

## Arquitetura Identificada

A arquitetura atual segue um desenho em camadas:

1. Entrada e bootstrap: `app.py` e `app_transcricao.spec`.
2. UI desktop: `src/ui/`, com `MainWindow`, `QueuePanel`, `SettingsModal` e `ResultViewerWindow`.
3. Orquestracao de fila: `src/core/queue_manager.py`.
4. Pipeline de job: `src/core/job_processor.py`.
5. Servicos de processamento: `TranscriptionService`, `ExtractionService`, `ExportService`, `CacheEngine`, `PersistentQueue`, `SettingsService`.
6. Modelos de dominio: `src/models/transcription_job.py`.
7. Enriquecimento AI-ready: `src/ai_ready/`, `src/semantic/`, `src/study/`.
8. Biblioteca e grafo: `src/library/`, `src/knowledge_graph/`, `src/knowledge/`.
9. Datasets: `src/datasets/`.
10. Persistencia local: JSON em `data/`.

## Modulos Principais

| Modulo | Responsabilidade |
|---|---|
| `app.py` | Bootstrap, tratamento de subprocessos no Windows, `PATH` local e inicio da GUI. |
| `src/ui/main_window.py` | Janela principal, toolbar, drag-and-drop, atalhos e callbacks thread-safe. |
| `src/ui/queue_panel.py` | Visualizacao e comandos da fila. |
| `src/ui/settings_modal.py` / `settings_panel.py` | Modal de configuracoes e controles avancados. |
| `src/ui/result_window.py` | Visualizacao/exportacao de resultado em janela secundaria. |
| `src/core/queue_manager.py` | Estado da fila, worker thread, recovery, cancelamento e callbacks. |
| `src/core/job_processor.py` | Pipeline por arquivo: cache, transcricao/extracao, exportacao, biblioteca/grafo/datasets. |
| `src/core/transcription_service.py` | Singleton Whisper, formatacao por segmentos e progresso. |
| `src/core/extraction_service.py` | TXT, PDF, DOCX, XLSX e OCR via Tesseract. |
| `src/core/export_service.py` | TXT/MD/JSON e pipeline AI-ready. |
| `src/cache/` | Hash, cache registry e leitura/gravação de estagios. |
| `src/ai_ready/` | Stages, templates, metadados, formatacao e export NotebookLM. |
| `src/semantic/` | Topicos, highlights, referencias biblicas, timestamps e indice. |
| `src/library/` | Catalogo, workspaces, colecoes, busca e relacionamentos. |
| `src/knowledge_graph/` | Grafo, nos, arestas, navegacao, busca e exportacao. |
| `src/study/` | Flashcards, quizzes, notas, revisoes e sumarizacao. |
| `src/datasets/` | Builders, registry, validacao, estatisticas e exportacao de datasets. |

## Fluxo Principal da Aplicacao

1. Usuario abre o app por `app.py`.
2. `app.py` injeta `bin/` no `PATH` e inicia `MainWindow`.
3. `MainWindow` valida disponibilidade do Whisper e carrega configuracoes.
4. Usuario adiciona arquivos por dialogo, pasta ou drag-and-drop.
5. `QueueManager.add_files()` valida tipo, caminho e monta `TranscriptionJob`.
6. `QueueManager.start_queue()` cria worker thread.
7. `JobProcessor.process()` decide entre cache, Whisper, extracao/OCR e exportacao.
8. Conteudo bruto pode ser enriquecido por `ExportService` e `src/ai_ready`.
9. Opcionalmente, modos avancados alimentam biblioteca, grafo, estudo e datasets.
10. Resultado e salvo no diretorio de saida, historico/cache/fila sao atualizados em `data/`.
11. UI recebe callbacks via `root.after()` para atualizar fila e status.

## Tecnologias Utilizadas

| Area | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ declarado; ambiente observado usa Python 3.14.4. |
| GUI | CustomTkinter, tkinterdnd2, Tkinter. |
| Transcricao | OpenAI Whisper, Torch, Tiktoken, FFmpeg. |
| Documentos | pdfplumber, python-docx, openpyxl. |
| OCR | pytesseract, Pillow, Tesseract externo/opcional. |
| Empacotamento | PyInstaller `onedir`, `app_transcricao.spec`, binarios em `bin/`. |
| Persistencia | JSON local em `data/`. |
| Testes | `unittest`. |

## Observacoes Importantes

- A documentacao aponta Python 3.10+, mas o ambiente local observado esta em Python 3.14.4, o que aumenta risco para Whisper/Torch e PyInstaller.
- O README referencia arquivos que nao existem na raiz atual, como `CHANGELOG.md`, `instalar_dependencias.bat` e `app_transcricao.py`.
- `data/` contem muitos artefatos de runtime e cache; isso deve ser tratado como dado local, nao como parte essencial do codigo.
- `src/__pycache__` e subpastas aparecem no workspace; sao artefatos gerados e candidatos a limpeza controlada em outra etapa.
