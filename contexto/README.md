# Memória do projeto CortexFlow

Esta pasta preserva contexto útil entre sessões de desenvolvimento, agentes e
colaboradores. Ela descreve onde o projeto está, para onde pretende ir, por que
decisões importantes foram tomadas e o que já foi realizado.

## Leitura recomendada

1. [`ESTADO_ATUAL.md`](ESTADO_ATUAL.md) — fotografia verificável do produto.
2. [`ROADMAP.md`](ROADMAP.md) — direção, prioridades e resultados desejados.
3. [`PLANO_EXECUCAO.md`](PLANO_EXECUCAO.md) — sequência prática de entregas.
4. [`DECISOES.md`](DECISOES.md) — decisões arquiteturais e operacionais.
5. [`DIARIO.md`](DIARIO.md) — histórico cronológico conciso do trabalho.

## O que pertence aqui

- Estado da arquitetura, qualidade, build e produto.
- Objetivos, prioridades, riscos e critérios de conclusão.
- Decisões que afetarão trabalhos futuros.
- Resumos de mudanças materiais e suas validações.

## O que não pertence aqui

- Segredos, tokens, credenciais ou dados pessoais.
- Conteúdo de transcrições e arquivos processados por usuários.
- Dumps extensos de terminal, diffs completos ou artefatos gerados.
- Planos especulativos sem indicação clara de que ainda não foram aprovados.

## Método de manutenção

- O estado atual deve conter fatos comprováveis, com data de revisão.
- O roadmap descreve resultados, não apenas listas de arquivos.
- Uma decisão não deve ser reescrita silenciosamente: marque-a como substituída e
  registre a nova decisão.
- O diário recebe entradas novas no topo e aponta para decisões quando necessário.
- Relatórios detalhados e pontuais continuam em `docs/`; esta pasta guarda apenas
  a síntese operacional.
