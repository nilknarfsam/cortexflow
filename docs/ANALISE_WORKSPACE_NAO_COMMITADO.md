# Analise do Workspace Nao Commitado

Data da analise: 2026-06-03  
Modo: seguro, sem commit, sem push, sem alteracao de codigo.

## Comandos Executados

```powershell
git status
git diff -- app.py app_transcricao.spec scripts/build_onedir.ps1
```

Tambem foram inspecionados `data/`, arquivos rastreados de `data/` via `git ls-files data`, diff dos JSONs principais de runtime e `.gitignore`.

## Estado Geral do Git

- Branch atual: `main`.
- Branch local esta 1 commit a frente de `origin/main`, referente ao commit local de documentacao anterior.
- Existem alteracoes nao staged em codigo, build e runtime.
- Existem muitos caches novos nao rastreados em `data/cache/`.
- Nenhum push foi realizado nesta etapa.

## Arquivos Alterados ou Nao Rastreados

### Alterados rastreados

| Arquivo | Tipo | Resumo |
|---|---|---|
| `app.py` | Codigo funcional | Ajuste no monkey-patch de `subprocess.Popen` no Windows. |
| `app_transcricao.spec` | Build/empacotamento | Adiciona checagem de dependencias no Python usado pelo PyInstaller. |
| `data/cache/.../whisper.txt` | Runtime/cache | Dois caches de transcricao rastreados foram alterados. |
| `data/cache_registry.json` | Runtime/cache | Registro de cache expandido fortemente, com muitos novos hashes e paths locais. |
| `data/historico_transcricoes.json` | Runtime/historico | Historico local alterado com transcricoes e caminhos de saida. |
| `data/queue_state.json` | Runtime/fila | Fila foi atualizada para estado vazio e nova metadata de sessao. |
| `data/settings.json` | Runtime/config local | Formato padrao mudou de `md` para `txt`; `knowledge_pipeline` mudou de `false` para `true`. |

### Nao rastreados

| Caminho | Tipo | Resumo |
|---|---|---|
| `scripts/build_onedir.ps1` | Script de build | Novo script auxiliar para build `onedir`, ainda nao rastreado. |
| `data/cache/*/` | Runtime/cache | Dezenas de diretorios novos de cache com `whisper.txt`. |

## Analise por Arquivo

### `app.py`

O que mudou:

- `creationflags` passou a preservar flags existentes e adicionar `CREATE_NO_WINDOW`.
- Foi adicionado `STARTUPINFO` com `SW_HIDE` para esconder janelas de subprocesso.
- Em build congelado, agora apenas `stdin` e redirecionado para `DEVNULL` quando nao informado.
- `stdout` e `stderr` deixaram de ser sobrescritos globalmente.

Interpretacao:

- Parece intencional.
- A mudanca corrige um risco real: Whisper/FFmpeg pode depender de `stdout=PIPE`; sobrescrever `stdout` por `DEVNULL` pode quebrar a transcricao no executavel.

Recomendacao:

- Manter, mas separar em commit proprio de `fix`, depois de teste manual com audio curto no executavel.

Risco:

- Medio. Toca comportamento global de subprocessos no Windows, area sensivel para Whisper, FFmpeg, Tesseract e abertura de pastas.

### `app_transcricao.spec`

O que mudou:

- Importa `importlib.util` e `sys`.
- Define lista de modulos obrigatorios: `customtkinter`, `tkinterdnd2`, `whisper`, `torch`, `tiktoken`, `PIL`, `pdfplumber`, `docx`, `openpyxl`, `pytesseract`.
- Falha cedo com `RuntimeError` caso o Python usado pelo PyInstaller nao tenha essas dependencias.

Interpretacao:

- Parece intencional.
- Ajuda a evitar builds incompletos ou feitos no Python errado.

Recomendacao:

- Manter, mas separar em commit de build/tooling.
- Validar se `docx` e o nome correto para checagem de `python-docx` no ambiente alvo.

Risco:

- Baixo a medio. Nao altera runtime do app, mas pode bloquear builds que antes passavam parcialmente.

### `scripts/build_onedir.ps1`

O que mudou:

- Arquivo novo, nao rastreado.
- Aceita `-PythonPath` ou variavel `CORTEXFLOW_PYTHON`.
- Valida versao Python menor que 3.13.
- Valida imports principais.
- Executa `scripts/copy_local_binaries.ps1`.
- Verifica `bin/ffmpeg.exe`.
- Executa PyInstaller com `--clean --noconfirm`.

Interpretacao:

- Parece intencional.
- E um script operacional util, mas ainda nao commitado.

Recomendacao:

- Separar em commit proprio junto com documentacao de build.
- Antes de commitar, revisar acentuacao/encoding e decidir se `Python < 3.13` e regra oficial.

Risco:

- Baixo. Nao roda automaticamente; so afeta quem chamar o script.

### `data/settings.json`

O que mudou:

- `default_export_format`: `md` -> `txt`.
- `features.knowledge_pipeline`: `false` -> `true`.

Interpretacao:

- Parece runtime local/acidental, causado por uso da aplicacao ou testes manuais.
- Nao parece mudanca de configuracao padrao do produto, pois defaults reais estao em `src/core/settings_service.py`.

Recomendacao:

- Nao commitar.
- Reverter ou ignorar em etapa separada, conforme politica de `data/`.

Risco:

- Medio. Se commitado, muda estado local inicial versionado e pode ativar pipeline de conhecimento indevidamente em outro ambiente.

### `data/queue_state.json`

O que mudou:

- Estado da fila anterior com jobs e transcricoes foi substituido por fila vazia.
- `session_completed` mudou para 14.
- `saved_at` atualizado.

Interpretacao:

- Runtime local/acidental.
- Contem/continha texto de transcricao, caminhos locais e estado de uso.

Recomendacao:

- Nao commitar.
- Deve ser tratado como arquivo de runtime, nao como codigo.

Risco:

- Alto se versionado, por expor conteudo transcrito, caminhos locais e estado do usuario.

### `data/cache_registry.json`

O que mudou:

- Registro expandiu de poucos itens para muitas entradas.
- Paths foram atualizados de `transcritor-universal` para `cortexflow`.
- Inclui nomes de aulas, tamanhos, timestamps e caminhos absolutos locais.

Interpretacao:

- Runtime/cache local.
- Alteracao provavelmente gerada por uso real do app.

Recomendacao:

- Nao commitar.
- Incluir em politica de ignore ou manter apenas exemplo separado, se necessario.

Risco:

- Alto. Contem metadados de arquivos e caminhos locais.

### `data/historico_transcricoes.json`

O que mudou:

- Historico recente foi atualizado com outras aulas, caminhos de saida, tempos, cache hit/miss e workspace.

Interpretacao:

- Runtime local/acidental.

Recomendacao:

- Nao commitar.
- Tratar como dado do usuario.

Risco:

- Alto. Expoe historico de uso e caminhos locais.

### `data/cache/*/whisper.txt`

O que mudou:

- Dois arquivos rastreados foram modificados.
- Muitos novos diretorios de cache foram criados e estao nao rastreados.
- A pasta `data/cache` contem 61 diretorios observados.

Interpretacao:

- Cache de transcricao local.
- Nao deve ser parte normal de commits.

Recomendacao:

- Nao commitar.
- Revisar `.gitignore` para ignorar `data/cache/`, mantendo no maximo um `.gitkeep` se a pasta precisar existir.

Risco:

- Alto. Pode conter transcricoes completas, dados privados e ruido pesado no Git.

## Analise da Pasta `data/`

### Contem cache?

Sim. `data/cache/` contem 61 diretorios de hash, cada um com `whisper.txt` ou artefatos similares. `data/cache_registry.json` indexa esses caches.

### Contem runtime local?

Sim. Foram observados:

- `data/settings.json`
- `data/queue_state.json`
- `data/historico_transcricoes.json`
- `data/cache_registry.json`
- `data/cache/*`
- `data/logs/app.log`
- `data/library/collections.json`
- `data/library/workspaces.json`

### Contem arquivos que nao deveriam ir para o Git?

Sim, principalmente:

- `data/cache/`
- `data/cache_registry.json`
- `data/historico_transcricoes.json`
- `data/queue_state.json`
- `data/settings.json`
- `data/logs/*.log` ja esta ignorado no `.gitignore`

`data/library/collections.json` e `data/library/workspaces.json` podem ser defaults do produto ou runtime local; precisam de decisao humana antes de mudar a politica.

### Precisa entrar no `.gitignore`?

Recomendacao: sim, em etapa separada e com cuidado, porque alguns arquivos de `data/` ja sao rastreados pelo Git.

Sugestao de politica futura:

```gitignore
data/cache/
data/cache_registry.json
data/historico_transcricoes.json
data/queue_state.json
data/settings.json
```

Possivel excecao:

```gitignore
!data/.gitkeep
!data/logs/.gitkeep
```

Antes de alterar `.gitignore`, Franklin deve decidir se `data/library/*.json` sao dados iniciais do produto ou runtime do usuario.

## Classificacao: Manter, Reverter ou Separar

| Item | Parece | Acao recomendada | Risco |
|---|---|---|---|
| `app.py` | Intencional | Separar em commit `fix` apos teste manual | Medio |
| `app_transcricao.spec` | Intencional | Separar em commit de build/tooling | Baixo/Medio |
| `scripts/build_onedir.ps1` | Intencional | Separar em commit de build/tooling, com revisao | Baixo |
| `data/settings.json` | Acidental/runtime | Nao commitar; reverter/ignorar em etapa segura | Medio |
| `data/queue_state.json` | Acidental/runtime | Nao commitar; reverter/ignorar em etapa segura | Alto |
| `data/cache_registry.json` | Acidental/runtime | Nao commitar; ignorar em politica futura | Alto |
| `data/historico_transcricoes.json` | Acidental/runtime | Nao commitar; ignorar em politica futura | Alto |
| `data/cache/*` | Acidental/runtime | Nao commitar; ignorar em politica futura | Alto |

## Recomendacao Clara para Franklin

Franklin, nao misture essas alteracoes em um unico commit.

Recomendacao de ordem:

1. Preservar temporariamente `app.py`, `app_transcricao.spec` e `scripts/build_onedir.ps1`, porque parecem corrigir/buildar o problema do executavel.
2. Nao commitar nada de `data/`.
3. Definir uma politica para `data/`: runtime local deve ficar fora do Git.
4. Em etapa separada, pedir ao Cursor para preparar um commit pequeno apenas com o hotfix de subprocess/build.
5. Depois, pedir outro commit separado para ajustar `.gitignore` e remover do indice os arquivos de runtime ja rastreados, sem apagar arquivos locais.

## Proxima Acao Sugerida para o Cursor

Tarefa sugerida:

> "Analise e prepare, sem push, dois commits separados: primeiro um commit de fix/build contendo apenas `app.py`, `app_transcricao.spec` e `scripts/build_onedir.ps1`; segundo, uma proposta de higiene de Git para `data/`, atualizando `.gitignore` e removendo do indice os arquivos de runtime sem apagar arquivos locais. Antes de qualquer commit, mostre exatamente o que sera staged."

## Observacao Final

Este relatorio foi gerado sem commit e sem push. Nenhum arquivo de codigo foi alterado nesta etapa.
