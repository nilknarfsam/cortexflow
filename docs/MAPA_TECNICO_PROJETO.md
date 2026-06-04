# Mapa Tecnico do Projeto CortexFlow

Data da analise: 2026-06-03

## Mapa de Pastas

| Pasta | Responsabilidade Atual | Observacoes |
|---|---|---|
| `src/` | Codigo principal da aplicacao. | Contem camadas de UI, core, IA local, biblioteca, grafo, datasets e estudo. |
| `tests/` | Testes unitarios existentes. | Cobertura focada em feature flag e formatacao/progresso Whisper. |
| `scripts/` | Automacoes auxiliares de build/binarios. | Contem copia de FFmpeg e script de build observado no workspace. |
| `docs/` | Relatorios tecnicos e documentacao operacional. | Ja contem relatorios de qualidade e UX. |
| `data/` | Persistencia local de runtime. | Settings, historico, fila, cache, logs e biblioteca; alto risco de misturar dados do usuario com repo. |
| `assets/` | Icones e assets visuais. | `icon.png` e `icon.ico`. |
| `bin/` | Binarios externos portateis. | `ffmpeg.exe`, `ffprobe.exe`; Tesseract nao observado. |
| `.venv/` | Ambiente virtual local. | Observado com Python 3.14.4. |
| `build/` / `dist/` | Saidas PyInstaller. | Artefatos gerados, ignorados pelo Git. |
| `_archive/` | Arquivos legados arquivados. | Referenciado por `agent.md`; fora do build principal. |

## Estrutura de `src/`

| Subpasta | Responsabilidade |
|---|---|
| `src/core/` | Orquestracao, servicos essenciais, configuracao, logging, erros, fila e exportacao. |
| `src/ui/` | Interface desktop atual e componentes visuais. |
| `src/ui/legacy_ui/` | Paineis avancados retirados da janela principal. |
| `src/models/` | Modelo `TranscriptionJob`, extensoes suportadas e status. |
| `src/cache/` | Hash SHA256, registro e estagios de cache. |
| `src/ai_ready/` | Pipeline de saida limpa, AI-ready, NotebookLM e Study Mode. |
| `src/semantic/` | Analise local baseada em regras: topicos, referencias, timestamps, highlights e indice. |
| `src/library/` | Biblioteca de conhecimento: catalogo, workspaces, colecoes, busca e relacoes. |
| `src/knowledge_graph/` | Grafo semantico local, navegacao, busca e exportacao. |
| `src/knowledge/` | Estatisticas de dashboard. |
| `src/datasets/` | Geracao, registro, validacao, estatisticas e exportacao de datasets. |
| `src/study/` | Materiais de estudo: notas, flashcards, quizzes, resumos e dificuldade. |
| `src/utils/` | Utilitarios auxiliares, como geracao de icone. |

## Arquivos Principais

| Arquivo | Papel |
|---|---|
| `app.py` | Entrada principal do app desktop. |
| `app_transcricao.spec` | Receita PyInstaller para build `onedir`. |
| `requirements.txt` | Dependencias de runtime. |
| `requirements-build.txt` | Dependencia de build (`pyinstaller`). |
| `agent.md` | Fonte de verdade operacional do projeto. |
| `README.md` | Documentacao publica do produto. |
| `src/core/job_processor.py` | Pipeline mais importante do processamento. |
| `src/core/queue_manager.py` | Estado e execucao da fila. |
| `src/core/settings_service.py` | Configuracoes, historico e caminhos de dados. |
| `src/core/transcription_service.py` | Whisper e formatacao de transcricao. |
| `src/ui/main_window.py` | Shell principal da GUI. |

## Dependencias Internas Entre Modulos

Fluxo simplificado:

```text
app.py
  -> src.ui.main_window.run_app
    -> MainWindow
      -> QueuePanel / SettingsModal / ResultViewerWindow
      -> QueueManager
        -> JobProcessor
          -> CacheEngine
          -> TranscriptionService
          -> ExtractionService
          -> ExportService
            -> ai_ready.pipeline
              -> semantic / study
          -> library / knowledge_graph / datasets (quando habilitados)
```

Dependencias transversais:

- `SettingsService` e usado por UI, fila, biblioteca e paths de dados.
- `TranscriptionJob` e compartilhado por UI, fila, persistencia e testes.
- `CacheEngine` participa da decisao de reprocessar ou reutilizar estagios.
- `ExportService` e ponte entre texto bruto e pipeline AI-ready.
- `get_library()` e `get_knowledge_graph()` funcionam como singletons/lazy loaders em pontos avancados.

## Dados e Persistencia

| Arquivo/Pasta | Uso |
|---|---|
| `data/settings.json` | Preferencias de UI, exportacao, modelo Whisper e feature flags. |
| `data/queue_state.json` | Recovery da fila. |
| `data/historico_transcricoes.json` | Historico recente. |
| `data/cache_registry.json` | Indice dos caches por hash. |
| `data/cache/*/whisper.txt` | Saidas intermediarias de transcricao. |
| `data/library/*.json` | Workspaces e colecoes. |
| `data/logs/app.log` | Log tecnico local. |

## Arquivos Pouco Utilizados ou Legados

| Arquivo/Pasta | Evidencia |
|---|---|
| `src/ui/result_panel.py` | Relatorio de UX indica que foi substituido por `result_window.py`. |
| `src/ui/document_detail_panel.py` | Usado por `legacy_ui/knowledge_workspace_panel.py`, nao pela janela principal. |
| `src/ui/components/knowledge_widgets.py` | Uso associado aos paineis legados. |
| `src/ui/legacy_ui/*.py` | Paineis preservados, mas nao montados por `main_window.py`. |
| `src/utils/create_icon.py` | Utilitario de geracao de assets, nao parte do fluxo de runtime. |
| `__pycache__/` em `src/` e `tests/` | Artefatos gerados, nao codigo fonte. |
