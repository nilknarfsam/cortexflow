# Instruções para agentes — CortexFlow

Este arquivo governa todo o repositório. Antes de alterar código ou documentação,
leia a memória do projeto em [`contexto/README.md`](contexto/README.md).

## Regras permanentes

1. Trabalhar e documentar em português do Brasil.
2. Consultar `contexto/ESTADO_ATUAL.md` e `contexto/ROADMAP.md` antes de planejar
   mudanças.
3. Fazer alterações pequenas, focadas e compatíveis com a arquitetura existente.
4. Não apagar dados locais, código legado ou decisões anteriores sem confirmação.
5. Não executar `git push` sem solicitação explícita.
6. Não criar commits automaticamente, salvo quando o usuário pedir.
7. Validar alterações proporcionalmente ao risco. O comando básico é:
   `python -m unittest discover -s tests -v`.
8. Nunca registrar segredos, credenciais, dados pessoais, transcrições ou caminhos
   privados na memória versionada.

## Atualização da memória

Ao concluir uma mudança material:

- Atualize `contexto/ESTADO_ATUAL.md` se o comportamento ou a arquitetura mudou.
- Atualize `contexto/ROADMAP.md` se uma iniciativa avançou, mudou de prioridade ou
  surgiu uma nova oportunidade.
- Registre decisões duradouras em `contexto/DECISOES.md`.
- Acrescente uma entrada curta em `contexto/DIARIO.md`.
- Não transforme o diário em cópia de diffs ou mensagens de commit; registre
  resultado, validação, risco e próximo passo.

## Fontes de verdade

Em caso de divergência, use esta ordem:

1. Código e testes atuais.
2. `AGENTS.md` e arquivos de `contexto/`.
3. `README.md`.
4. Relatórios históricos em `docs/`.
5. `agent.md`, mantido temporariamente como documento legado.
