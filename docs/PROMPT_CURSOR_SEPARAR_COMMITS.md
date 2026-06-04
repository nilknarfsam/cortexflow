# Prompt para o Cursor Separar Commits com Segurança

Use este prompt no Cursor dentro do projeto CortexFlow.

---

Voce esta trabalhando no projeto CortexFlow em:

```text
C:\src\projects\cortexflow
```

## Modo de Trabalho Seguro

Regras obrigatorias:

- NAO fazer push.
- NAO publicar nada no GitHub.
- NAO instalar dependencias.
- NAO apagar arquivos locais.
- NAO usar `git reset --hard`.
- NAO usar `git clean`.
- NAO usar `git checkout --` / `git restore` em arquivos do usuario sem autorizacao explicita.
- NAO misturar alteracoes de codigo/build com dados de runtime em `data/`.
- Fazer apenas commits locais.
- Antes de cada commit, mostrar obrigatoriamente:

```powershell
git diff --cached --stat
git diff --cached --name-status
```

- Rodar testes antes dos commits funcionais:

```powershell
python -m unittest discover -s tests -v
```

- Se algum comando falhar, parar e relatar exatamente o erro.

## Contexto Atual Esperado

Ha alteracoes nao commitadas em:

- `app.py`
- `app_transcricao.spec`
- `scripts/build_onedir.ps1`
- varios arquivos em `data/`

O objetivo e separar com seguranca em tres commits locais:

1. Hotfix de subprocessos Windows/PyInstaller.
2. Build/tooling do PyInstaller onedir.
3. Higiene de dados locais de runtime em `data/`.

O diretorio `data/` contem runtime local/cache/historico/fila/settings. Esses dados NAO devem entrar nos commits 1 e 2.

## Preparacao Obrigatoria

Execute:

```powershell
git status
git diff -- app.py app_transcricao.spec scripts/build_onedir.ps1
git status --ignored
```

Leia tambem:

```text
docs/ANALISE_WORKSPACE_NAO_COMMITADO.md
docs/RELATORIO_EXECUTIVO_PARA_FRANKLIN.md
agent.md
```

Confirme no seu resumo inicial:

- branch atual;
- se ha arquivos staged antes de comecar;
- quais arquivos estao modificados;
- quais arquivos em `data/` aparecem modificados ou nao rastreados;
- que nenhum push sera feito.

## Commit 1 - Hotfix

Objetivo: commitar somente a correcao de subprocessos no Windows/PyInstaller.

Arquivos permitidos:

```text
app.py
```

Passos:

1. Revisar somente o diff de `app.py`:

```powershell
git diff -- app.py
```

2. Confirmar que a alteracao preserva pipes de `stdout`/`stderr` para FFmpeg/Whisper e apenas evita janelas de subprocesso no Windows.

3. Rodar testes:

```powershell
python -m unittest discover -s tests -v
```

4. Fazer stage somente de `app.py`:

```powershell
git add app.py
```

5. Mostrar antes do commit:

```powershell
git diff --cached --stat
git diff --cached --name-status
```

6. Verificar que o staged contem apenas:

```text
app.py
```

7. Criar commit local:

```powershell
git commit -m "fix: corrige subprocessos no Windows e PyInstaller"
```

8. Rodar:

```powershell
git status
```

Nao inclua `app_transcricao.spec`, `scripts/build_onedir.ps1` ou `data/` neste commit.

## Commit 2 - Build/tooling

Objetivo: commitar somente ajustes de build e script onedir.

Arquivos permitidos:

```text
app_transcricao.spec
scripts/build_onedir.ps1
```

Passos:

1. Revisar somente:

```powershell
git diff -- app_transcricao.spec scripts/build_onedir.ps1
```

Observacao: se `scripts/build_onedir.ps1` for arquivo novo e `git diff` nao mostrar conteudo, use leitura normal:

```powershell
Get-Content scripts\build_onedir.ps1
```

2. Confirmar que:

- `app_transcricao.spec` apenas valida dependencias no Python usado pelo PyInstaller;
- `scripts/build_onedir.ps1` apenas orquestra validacao/build;
- nenhum arquivo em `data/` sera staged.

3. Rodar testes novamente:

```powershell
python -m unittest discover -s tests -v
```

4. Fazer stage somente dos dois arquivos:

```powershell
git add app_transcricao.spec scripts\build_onedir.ps1
```

5. Mostrar antes do commit:

```powershell
git diff --cached --stat
git diff --cached --name-status
```

6. Verificar que o staged contem apenas:

```text
app_transcricao.spec
scripts/build_onedir.ps1
```

7. Criar commit local:

```powershell
git commit -m "build: adiciona validação e script onedir"
```

8. Rodar:

```powershell
git status
```

Nao inclua `app.py` nem `data/` neste commit.

## Commit 3 - Dados locais

Objetivo: proteger dados locais de runtime/cache/logs/fila/settings contra commits futuros.

Arquivos/padroes a revisar:

```text
.gitignore
data/
```

Regras obrigatorias:

- NAO apagar arquivos locais.
- Se arquivos rastreados em `data/` precisarem sair do Git, usar apenas `git rm --cached`.
- Nao remover do disco os caches, historicos, settings ou fila local do Franklin.
- Nao incluir conteudo de `data/cache/`, `data/cache_registry.json`, `data/historico_transcricoes.json`, `data/queue_state.json` ou `data/settings.json` no commit.

Passos:

1. Revisar `.gitignore`:

```powershell
Get-Content .gitignore
```

2. Revisar arquivos rastreados em `data/`:

```powershell
git ls-files data
```

3. Propor/editar `.gitignore` para ignorar runtime local. Sugestao base:

```gitignore
data/cache/
data/cache_registry.json
data/historico_transcricoes.json
data/queue_state.json
data/settings.json
```

Manter excecoes se necessario:

```gitignore
!data/.gitkeep
!data/logs/.gitkeep
```

4. Antes de remover qualquer arquivo do indice, mostrar lista exata dos arquivos rastreados em `data/` que pretende remover do indice.

5. Remover do indice somente arquivos de runtime/cache locais. Exemplo, ajuste conforme `git ls-files data`:

```powershell
git rm --cached data/cache_registry.json data/historico_transcricoes.json data/queue_state.json data/settings.json
git rm --cached -r data/cache
```

Importante: `git rm --cached` remove apenas do indice. Nao use comando que apague arquivos locais.

6. Avaliar separadamente `data/library/collections.json` e `data/library/workspaces.json`.

Decisao recomendada:

- Se forem defaults do produto, manter rastreados.
- Se forem runtime local do usuario, remover do indice em commit separado ou incluir neste commit somente apos confirmar explicitamente.

7. Fazer stage somente de `.gitignore` e das remocoes do indice em `data/`:

```powershell
git add .gitignore
```

8. Mostrar antes do commit:

```powershell
git diff --cached --stat
git diff --cached --name-status
```

9. Verificar que o staged contem apenas:

- `.gitignore`;
- remocoes do indice dos arquivos de runtime em `data/`, se houver.

10. Criar commit local:

```powershell
git commit -m "chore: ignora dados locais de runtime"
```

11. Rodar:

```powershell
git status --ignored
```

## Validacoes Finais

Ao terminar, gerar resumo final contendo:

- commits criados, com hash curto e mensagem;
- testes executados e resultado;
- arquivos ainda modificados ou nao rastreados;
- status de `data/` depois da higiene;
- confirmacao explicita: "Nenhum push foi realizado.";
- pendencias para Franklin/Codex.

## Resultado Esperado

Ao final, deve haver ate tres commits locais:

```text
fix: corrige subprocessos no Windows e PyInstaller
build: adiciona validação e script onedir
chore: ignora dados locais de runtime
```

Se qualquer etapa parecer arriscada ou diferente do esperado, pare antes do commit e peca confirmacao.
