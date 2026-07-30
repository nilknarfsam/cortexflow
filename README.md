# CortexFlow

> Aplicação desktop local para transformar áudios, vídeos e documentos em conteúdo
> estruturado, pesquisável e pronto para fluxos de conhecimento.

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Qualidade](https://github.com/nilknarfsam/cortexflow/actions/workflows/quality.yml/badge.svg)](https://github.com/nilknarfsam/cortexflow/actions/workflows/quality.yml)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-412991?logo=openai&logoColor=white)](https://github.com/openai/whisper)
[![Processamento local](https://img.shields.io/badge/processamento-local-2E8B57)](#privacidade)
[![Versão](https://img.shields.io/badge/versão-3.0.4-6C63FF)](https://github.com/nilknarfsam/cortexflow)

CortexFlow combina transcrição com OpenAI Whisper, extração de documentos, fila
persistente e exportação estruturada em uma interface para Windows. O processamento
principal acontece no computador do usuário: o projeto não depende de uma API externa
para transcrever os arquivos.

## Visão geral

- Transcrição local de áudio e vídeo com Whisper e FFmpeg.
- Fila em lote com seleção, progresso, cancelamento e recuperação de sessão.
- Extração de texto de PDF, DOCX, XLSX, TXT e imagens por OCR.
- Cache por conteúdo para evitar processamento repetido.
- Exportação em TXT, Markdown e JSON.
- Modos de estruturação Raw, Clean, AI Ready, NotebookLM e Study Mode.
- Diagnóstico integrado de dependências e do ambiente local.
- Persistência JSON com gravação atômica para proteger configurações, fila e cache.

## Requisitos

| Componente | Obrigatório | Finalidade |
|---|:---:|---|
| Windows 10 ou 11 | Sim | Plataforma atualmente validada |
| Python 3.12 | Sim | Runtime oficial do projeto |
| FFmpeg e FFprobe | Sim | Leitura e conversão de áudio e vídeo |
| Tesseract OCR | Não | Extração de texto de imagens |
| GPU compatível com CUDA | Não | Aceleração opcional da transcrição |

O primeiro uso de um modelo Whisper pode exigir conexão com a internet para baixá-lo.
Depois do download, a transcrição pode ser executada localmente.

## Instalação

Abra o PowerShell e execute:

```powershell
git clone https://github.com/nilknarfsam/cortexflow.git
cd cortexflow

py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Instale o FFmpeg pelo gerenciador do Windows:

```powershell
winget install --id Gyan.FFmpeg -e
```

Feche e reabra o terminal após a instalação. Confirme o ambiente:

```powershell
ffmpeg -version
ffprobe -version
```

Como alternativa para desenvolvimento e empacotamento, os executáveis podem ser
copiados para `bin/`:

```powershell
.\scripts\copy_local_binaries.ps1
```

Os binários locais não são versionados por causa do tamanho.

## Execução

Com o ambiente virtual ativo:

```powershell
python app.py
```

Na interface:

1. Adicione arquivos pelo seletor ou arraste-os para a fila.
2. Ajuste modelo, idioma, formato e modo de exportação nas configurações.
3. Selecione os itens desejados e inicie o processamento.
4. Consulte os resultados e arquivos exportados pela própria aplicação.

Atalhos principais:

| Atalho | Ação |
|---|---|
| `Ctrl+O` | Adicionar arquivos |
| `Ctrl+T` | Iniciar a fila |
| `Ctrl+E` | Exportar |
| `Ctrl+,` | Abrir configurações |

## Formatos

| Categoria | Extensões |
|---|---|
| Áudio | `.mp3`, `.wav`, `.m4a`, `.flac` |
| Vídeo | `.mp4`, `.avi`, `.mov`, `.mkv` |
| Documentos | `.txt`, `.pdf`, `.docx`, `.xlsx` |
| Imagens com OCR | `.jpg`, `.jpeg`, `.png` |

## Diagnóstico

Em **Configurações → Mostrar configurações avançadas → Executar diagnóstico**, o
CortexFlow verifica:

- FFmpeg e FFprobe;
- Tesseract;
- Whisper e PyTorch;
- disponibilidade do modelo base;
- permissão de gravação da pasta de dados.

O relatório pode ser copiado para suporte sem incluir caminhos locais, conteúdo
processado ou credenciais.

## Desenvolvimento e qualidade

Instale as dependências de desenvolvimento:

```powershell
python -m pip install -r requirements-dev.txt
```

Execute a validação completa:

```powershell
python -m ruff check app.py src tests
python -m coverage run -m unittest discover -s tests -v
python -m coverage report
python -m compileall -q app.py src tests
```

O pipeline de integração contínua executa essas verificações no Windows com Python
3.12. A cobertura automatizada concentra-se inicialmente em `src/core`, `src/cache`
e `src/models`, com piso de 55%.

## Empacotamento para Windows

O build utiliza PyInstaller em modo *one-directory*:

```powershell
python -m pip install -r requirements-build.txt
.\scripts\copy_local_binaries.ps1
.\scripts\build_onedir.ps1
```

O artefato é criado em `dist/CortexFlow/`. No final do script, os binários
obrigatórios são conferidos e `CortexFlow.exe --smoke-test` valida os imports
essenciais sem abrir a interface.

## Arquitetura

```text
app.py
└── src/
    ├── ui/                 interface e componentes visuais
    ├── core/               fila, processamento, extração e exportação
    ├── cache/              identificação e reutilização de resultados
    ├── models/             modelos de domínio
    ├── ai_ready/           estruturação para IA e NotebookLM
    ├── semantic/           tópicos, referências e timestamps
    ├── study/              resumos, revisões, quizzes e flashcards
    ├── datasets/           construção e validação de datasets
    ├── library/            catálogo, coleções e espaços de trabalho
    └── knowledge_graph/    relações e navegação do conhecimento
```

Os dados de execução ficam sob `data/` e não devem ser enviados ao repositório.
A memória técnica e o planejamento vivo do projeto ficam em [`contexto/`](contexto/README.md).

## Privacidade

O CortexFlow foi projetado para processar arquivos localmente. Transcrições, cache,
histórico e configurações permanecem no computador do usuário. A obtenção inicial
de dependências e modelos pode usar a internet, mas o fluxo de transcrição não envia
o conteúdo para uma API do projeto.

Antes de compartilhar logs ou relatórios, ainda é recomendável revisar o conteúdo
gerado pelo sistema operacional e por ferramentas externas.

## Estado do projeto

A versão 3.0.4 está em evolução ativa. A fila, a persistência, o cache, a exportação
e o diagnóstico possuem testes automatizados, mas ainda existem áreas avançadas com
cobertura menor e módulos de interface legada preservados para migração gradual.

Consulte:

- [`contexto/ESTADO_ATUAL.md`](contexto/ESTADO_ATUAL.md) — fotografia técnica atual;
- [`contexto/ROADMAP.md`](contexto/ROADMAP.md) — direção de evolução;
- [`contexto/DECISOES.md`](contexto/DECISOES.md) — decisões duradouras;
- [`docs/`](docs/) — relatórios históricos e análises anteriores.

## Contribuição

Antes de alterar o projeto, leia [`AGENTS.md`](AGENTS.md). Prefira mudanças pequenas,
compatíveis com a arquitetura existente e acompanhadas de testes proporcionais ao
risco. Pull requests devem manter as verificações de qualidade aprovadas.

## Licença

Este repositório ainda não possui um arquivo de licença. Até que uma licença seja
definida pelo responsável, não presuma autorização para uso, modificação ou
redistribuição fora dos direitos concedidos pela legislação aplicável.

---

<p align="center">
  <strong>CortexFlow 3.0.4</strong><br>
  Transcrição local, organização do conhecimento e exportação estruturada.
</p>
