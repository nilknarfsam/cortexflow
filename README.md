# CortexFlow

**Plataforma de preparação inteligente de conhecimento para IA.**

Transforme conteúdos brutos (áudio, vídeo, documentos, OCR) em Markdown e formatos AI-ready para NotebookLM, GPT Projects, RAG, Obsidian e agentes IA.

> Ponto de entrada: `app.py`

---

## Recursos

* **Transcrição (Whisper):** MP3, WAV, M4A, FLAC, MP4, AVI, MOV, MKV
* **Textos:** TXT, PDF, DOCX, XLSX
* **OCR em imagens:** JPG, JPEG, PNG (via Tesseract)
* **Fila:** vários arquivos com status (aguardando, processando, concluído, erro, cancelado)
* **Controles:** iniciar/cancelar fila, barra de progresso geral, contadores por status
* **Saída automática:** mesma pasta do arquivo ou pasta global; botão **Abrir pasta de saída**
* **Idiomas:** detecção automática ou seleção manual (pt, en, es, fr, de, it, ru, zh)
* **UX:** arrastar & soltar, preview inteligente para textos grandes, tema escuro/claro
* **Exportação:** TXT, JSON, Markdown (automática e manual)
* **Histórico:** transcrições e sessões parciais em `data/historico_transcricoes.json`
* **Log técnico:** `data/logs/app.log` (erros e eventos da fila)
* **Design System:** tokens visuais premium em `src/ui/design/`
* **Pipeline AI-ready:** modos Raw, Clean, AI Ready e NotebookLM
* **Semantic Intelligence:** referências, highlights, tópicos, índice e chunking

---

## Estrutura do projeto

```
app.py
src/
  semantic/                    # Semantic Intelligence Engine
    references/
    highlights/
    indexing/
    timestamps/
    topics/
  ai_ready/                    # Pipeline AI-ready
    metadata/                  # YAML frontmatter
    templates/                 # Sermão, podcast, aula, genérico
    formatters/                # Markdown beautifier
    chunking/                  # Fundação RAG
    exporters/                 # NotebookLM exporter
    pipeline.py
    stages.py
  core/
    transcription_service.py   # Whisper (singleton)
    extraction_service.py      # TXT, PDF, DOCX, XLSX, OCR
    export_service.py
    queue_manager.py
    settings_service.py
    log_service.py
    job_errors.py
  models/
    transcription_job.py
  ui/
    design/                    # Design System CortexFlow
      colors.py
      fonts.py
      spacing.py
      theme_manager.py
    main_window.py
    queue_panel.py
    settings_panel.py
    result_panel.py
data/
  settings.json
  historico_transcricoes.json
  logs/app.log
```

---

## Requisitos (Windows)

### 1) Python 3.10+

* Baixe e instale o Python (marque **“Add Python to PATH”**).
* [https://www.python.org/downloads/](https://www.python.org/downloads/)

### 2) FFmpeg (para Whisper)

* Adicione o diretório `bin` do FFmpeg ao PATH.
* [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
* Builds Windows: [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)

### 3) Tesseract OCR (para imagens)

* Instale com os idiomas desejados (ex.: Portuguese).
* [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

> Ex.: adicione `C:\Program Files\Tesseract-OCR\` ao PATH.

### 4) Dependências Python

```bash
pip install -r requirements.txt
```

Ou execute `instalar_dependencias.bat`.

---

## Como executar

Na pasta do projeto:

```bash
python app.py
```

Compatível com o comando legado:

```bash
python app_transcricao.py
```

---

## Como usar

1. Abra o app e ajuste **tema**, **idioma** e **formato padrão** no painel esquerdo.
2. **Adicione arquivos** (botão ou drag & drop) — entram na fila de processamento.
3. Opcional: defina uma **pasta global de saída** ou deixe na mesma pasta do arquivo.
4. Clique em **Iniciar Fila** para processar todos os itens aguardando.
5. Use **Cancelar Fila** para interromper após o item atual; o progresso parcial fica no histórico.
6. Acompanhe **contadores** e a **barra de progresso** acima da lista.
7. Selecione um item para ver o resultado (preview truncado em textos grandes; use **Carregar texto completo**).
8. **Abrir pasta de saída** abre o Explorer na pasta do item selecionado ou na pasta global.
9. Consulte o histórico no painel de configurações; detalhes técnicos em `data/logs/app.log`.

---

## Atalhos

* **Ctrl + O** → Adicionar arquivos
* **Ctrl + T** → Iniciar fila
* **Ctrl + E** → Exportar (diálogo de formato)
* **Ctrl + Q** → Fechar app

---

## Formatos suportados

* **Áudio:** `.mp3`, `.wav`, `.m4a`, `.flac`
* **Vídeo:** `.mp4`, `.avi`, `.mov`, `.mkv`
* **Texto:** `.txt`, `.pdf`, `.docx`, `.xlsx`
* **Imagem (OCR):** `.jpg`, `.jpeg`, `.png`

---

## Configuração PATH no Windows

### FFmpeg

```bash
ffmpeg -version
```

### Tesseract

```bash
tesseract --version
```

Se necessário:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## Problemas comuns

* **Whisper não instalado** → `pip install -r requirements.txt`
* **ffmpeg not found** → FFmpeg não está no PATH
* **tesseract not installed** → Tesseract não está no PATH
* **PDF sem texto** → PDF é imagem; use OCR em imagem exportada ou ferramenta dedicada

---

## Using CortexFlow with NotebookLM

O CortexFlow transforma conteúdo bruto em **conhecimento estruturado** pronto para importar no [NotebookLM](https://notebooklm.google.com), GPT Projects, RAG e Obsidian.

### Pipeline de exportação

```
RAW → CLEAN → AI_READY → SEMANTIC → NOTEBOOKLM
```

| Modo | Descrição |
|------|-----------|
| **Raw** | Texto original (comportamento legado) |
| **Clean** | Texto normalizado e embelezado |
| **AI Ready** | Markdown com seções semânticas (resumo, pontos, frases, referências) |
| **NotebookLM** | YAML metadata + markdown estruturado otimizado para IA |

Configure **Modo de exportação** e **Tipo de conteúdo** no painel esquerdo. A escolha é salva em `data/settings.json`.

### Estrutura YAML (frontmatter)

Documentos no modo NotebookLM incluem metadata opcional:

```yaml
---
title: Nome do arquivo
source: /caminho/origem.mp3
language: pt
content_type: sermon
pipeline_stage: notebooklm
topics:
  - fé
tags:
  - evangelho
---
```

Campos ausentes são omitidos automaticamente.

### Templates disponíveis

* **generic** — Resumo, Conteúdo, Pontos, Frases, Referências, Tags
* **sermon** — Estrutura da Mensagem, Contexto Bíblico, Aplicações, Referências Bíblicas
* **podcast** — Timestamps, Pontos principais
* **course** — Exercícios e reflexões para aulas

### Dica de uso

1. Selecione modo **NotebookLM** e formato **md**.
2. Escolha o template adequado (ex.: `sermon` para pregações).
3. Processe a fila e importe o `.md` gerado no NotebookLM.

Todo o processamento é **local e determinístico** — sem APIs externas.

---

## Semantic Intelligence Engine

A camada semântica do CortexFlow (`src/semantic/`) transforma texto estruturado em **conhecimento navegável** — 100% local, sem APIs externas.

### Capacidades

| Módulo | Função |
|--------|--------|
| **Referências bíblicas** | Detecta João 11:25, Romanos 8:28, Salmos 91, etc. |
| **Highlights** | Extrai frases marcantes por heurísticas de impacto |
| **Tópicos** | Identifica fé, graça, salvação, ressurreição, etc. |
| **Índice automático** | Gera `# Índice` a partir de títulos e timestamps |
| **Timestamps** | Formata `## [00:14:22] Título do segmento` |
| **Chunking semântico** | Prepara blocos RAG-ready com IDs, tópicos e relação pai/filho |

### Pipeline semântico

Ativo automaticamente no modo **NotebookLM**. O preview exibe badge **Semantic Ready** com contagem de referências, highlights, chunks e tópicos detectados.

### Preparação RAG

Cada chunk exporta estrutura:

```json
{
  "chunk_id": "chunk-a1b2c3d4",
  "title": "O chamado de Lázaro",
  "start_timestamp": "00:12:14",
  "topics": ["fé", "ressurreição"],
  "content": "..."
}
```

Embeddings e busca vetorial virão em sprints futuras.

---

## Posicionamento

CortexFlow não é apenas um transcritor. É uma **plataforma de ingestão, estruturação e preparação de conhecimento para IA**.

---

## Changelog

Veja [CHANGELOG.md](CHANGELOG.md).
