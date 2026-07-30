# Registro de decisões

Decisões mais recentes devem ser adicionadas no topo. Use um identificador
sequencial e preserve decisões substituídas como histórico.

## DEC-002 — Preservar patch global de subprocessos com isolamento

- Data: 2026-07-29
- Status: aceita
- Contexto: Whisper e pytesseract criam subprocessos internamente e não oferecem
  um ponto único do CortexFlow para definir flags de janela no Windows.
- Decisão: manter a substituição de `subprocess.Popen`, movendo-a para um módulo
  idempotente e testado que preserva argumentos explícitos do chamador.
- Consequências: FFmpeg e Tesseract continuam sem janelas de console no aplicativo
  windowless; a alteração global permanece explícita, limitada ao Windows e
  protegida por testes de flags, `stdin`, `startupinfo` e reaplicação.

## DEC-001 — Memória versionada separada das instruções

- Data: 2026-07-28
- Status: aceita
- Contexto: o antigo `agent.md` reúne regras, fotografia técnica, roadmap e diário
  em um único documento extenso, dificultando atualização e identificação da
  fonte de verdade.
- Decisão: manter `AGENTS.md` na raiz como protocolo operacional e usar a pasta
  `contexto/` para estado, roadmap, decisões e diário.
- Consequências: agentes recebem instruções no escopo correto do repositório; a
  memória fica mais fácil de revisar e atualizar. O `agent.md` permanece
  temporariamente como histórico, com prioridade inferior.

## Modelo para novas decisões

```text
## DEC-NNN — Título

- Data: AAAA-MM-DD
- Status: proposta | aceita | substituída
- Contexto:
- Decisão:
- Consequências:
- Substitui: DEC-NNN (quando aplicável)
```
