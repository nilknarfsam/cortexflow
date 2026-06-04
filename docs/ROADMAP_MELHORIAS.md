# Roadmap de Melhorias do CortexFlow

Data da analise: 2026-06-03

## Prioridade Alta

### Sprint A1 - Ambiente e Build Reprodutivel

Objetivo: garantir que o app seja empacotado sempre com Python e dependencias compativeis.

Arquivos envolvidos:

- `README.md`
- `requirements.txt`
- `requirements-build.txt`
- `app_transcricao.spec`
- `scripts/`
- novo documento de release em `docs/`

Risco estimado: medio. Afeta build, mas nao precisa alterar regra de negocio.

Entregas sugeridas:

- Fixar Python recomendado: 3.10, 3.11 ou 3.12.
- Documentar criacao de venv limpa.
- Validar FFmpeg/Whisper/Torch antes do build.
- Criar checklist de teste manual do executavel.

### Sprint A2 - Diagnostico de Transcricao e Dependencias Externas

Objetivo: reduzir falhas silenciosas de Whisper, FFmpeg e Tesseract.

Arquivos envolvidos:

- `app.py`
- `src/core/transcription_service.py`
- `src/core/extraction_service.py`
- `src/core/job_errors.py`
- `src/core/log_service.py`
- `src/ui/settings_modal.py` ou nova area de diagnostico

Risco estimado: alto. Mexe no fluxo critico de transcricao.

Entregas sugeridas:

- Diagnostico visivel para FFmpeg/Tesseract/modelo Whisper.
- Mensagens de erro mais acionaveis.
- Log tecnico com paths de binarios usados.
- Teste com arquivo de audio curto.

### Sprint A3 - Higiene de Dados Locais

Objetivo: impedir que cache, historico e logs entrem em commits por acidente.

Arquivos envolvidos:

- `.gitignore`
- `data/`
- `src/core/settings_service.py`
- `src/cache/`
- docs de operacao

Risco estimado: medio. Nao apagar dados sem backup/decisao humana.

Entregas sugeridas:

- Confirmar politica de versionamento de `data/`.
- Documentar quais arquivos sao runtime.
- Criar rotina segura de limpeza futura, com confirmacao.

## Prioridade Media

### Sprint M1 - Testes do Core

Objetivo: cobrir fila, cache, persistencia e exportacao.

Arquivos envolvidos:

- `tests/`
- `src/core/queue_manager.py`
- `src/core/job_processor.py`
- `src/core/persistent_queue.py`
- `src/cache/`
- `src/core/export_service.py`

Risco estimado: baixo a medio. Preferir mocks/fakes para evitar Whisper real.

Entregas sugeridas:

- Testes de fila: adicionar, remover, cancelar, recovery.
- Testes de cache hit/miss/partial.
- Testes de export raw/md/json/AI-ready.
- Testes de erro classificado.

### Sprint M2 - Documentacao Publica Coerente

Objetivo: alinhar README, agent.md e codigo real.

Arquivos envolvidos:

- `README.md`
- `agent.md`
- `docs/`
- `bin/README.md`

Risco estimado: baixo. Documentacao apenas.

Entregas sugeridas:

- Corrigir referencias inexistentes.
- Atualizar nome do repo e comandos.
- Documentar build `onedir` e portable.
- Explicar limitações de OCR/Tesseract.

### Sprint M3 - Observabilidade Local

Objetivo: facilitar suporte sem abrir console.

Arquivos envolvidos:

- `src/core/log_service.py`
- `src/ui/settings_panel.py`
- `src/ui/settings_modal.py`
- `src/ui/queue_panel.py`

Risco estimado: medio.

Entregas sugeridas:

- Botao "abrir log tecnico".
- Botao "copiar diagnostico".
- Status de dependencias externas.
- Registro de versao Python e build.

## Prioridade Baixa

### Sprint B1 - Organizar Legados de UI

Objetivo: decidir destino dos paineis avancados e reduzir confusao.

Arquivos envolvidos:

- `src/ui/result_panel.py`
- `src/ui/document_detail_panel.py`
- `src/ui/components/knowledge_widgets.py`
- `src/ui/legacy_ui/`
- `docs/UI_CLEANUP_REPORT.md`

Risco estimado: medio se remover; baixo se apenas documentar/mover.

Entregas sugeridas:

- Inventario final de uso.
- Decidir manter, mover para `_archive` ou reativar.
- Atualizar docs de arquitetura.

### Sprint B2 - Separar Contratos Internos

Objetivo: melhorar manutencao sem grande refatoracao.

Arquivos envolvidos:

- `src/core/`
- `src/models/`
- possivel novo `src/core/protocols.py`

Risco estimado: medio.

Entregas sugeridas:

- Protocols para transcricao, extracao, exportacao e cache.
- Facilitar testes com fakes.
- Evitar refatoracao ampla inicialmente.

### Sprint B3 - Polimento de Interface

Objetivo: deixar uso diario mais claro e profissional.

Arquivos envolvidos:

- `src/ui/main_window.py`
- `src/ui/queue_panel.py`
- `src/ui/result_window.py`
- `src/ui/design/`

Risco estimado: baixo a medio.

Entregas sugeridas:

- Rever textos corrompidos/acentuacao.
- Melhorar densidade e estados vazios.
- Acoes de erro: tentar novamente, abrir log, abrir pasta.

## Proxima Tarefa Ideal

A proxima tarefa ideal e uma sprint pequena de documentacao/build: alinhar README e criar checklist de release com Python recomendado, sem mexer no motor. Isso reduz risco imediato antes de novas alteracoes funcionais.
