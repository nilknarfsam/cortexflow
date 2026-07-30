# Roadmap

Última revisão: 2026-07-29

Execução detalhada: [`PLANO_EXECUCAO.md`](PLANO_EXECUCAO.md).

## Visão

Evoluir o CortexFlow de uma aplicação local funcional para um produto desktop
confiável, reproduzível e fácil de manter, sem perder o processamento offline e a
simplicidade do fluxo principal.

## Horizonte 1 — Base confiável

Objetivo: toda alteração deve receber feedback automatizado rápido.

- [Concluído] Corrigir instalação, links e comandos do README.
- [Concluído] Adotar `pyproject.toml` como configuração central.
- [Concluído] Configurar lint, formatação e cobertura.
- [Concluído] Criar CI para versões de Python oficialmente suportadas.
- [Concluído] Fixar ou limitar versões de dependências.
- [Concluído] Cobrir fila, persistência, cache, exportação e classificação de erros.

Critério de conclusão: CI obrigatória e verde, documentação executável e cobertura
significativa do núcleo sem carregar um modelo Whisper real.

## Horizonte 2 — Runtime diagnosticável

Objetivo: reduzir falhas difíceis de explicar no computador do usuário.

- [Concluído] Diagnosticar FFmpeg, FFprobe, Tesseract, Python e modelo Whisper.
- [Concluído] Exibir mensagens acionáveis e opção de copiar diagnóstico.
- [Concluído] Padronizar logs sem expor conteúdo sensível.
- [Concluído] Criar smoke test do build one-directory.
- [Concluído] Revisar o patch global de `subprocess.Popen`.

O horizonte foi concluído em 2026-07-29. O patch foi mantido por atender
subprocessos internos de terceiros, mas agora está isolado, idempotente e testado.

Critério de conclusão: problemas comuns de ambiente podem ser identificados pela
interface e reproduzidos por um relatório técnico seguro.

## Horizonte 3 — Arquitetura sustentável

Objetivo: facilitar testes e evolução sem uma reescrita ampla.

- Dividir o `JobProcessor` em etapas menores e testáveis.
- Separar persistência, migração e preferências no `SettingsService`.
- Introduzir contratos para transcrição, extração, cache e exportação.
- Definir o destino da UI legada.
- Isolar melhor recursos avançados de conhecimento do fluxo básico.

Critério de conclusão: o fluxo principal pode ser exercitado com fakes e mudanças
em uma etapa não exigem carregar todo o sistema.

## Possibilidades futuras

Estas ideias ainda não são compromissos:

- CLI reutilizando o mesmo núcleo da aplicação.
- Processamento paralelo seletivo para documentos leves.
- Perfis de exportação reutilizáveis.
- Atualização assistida e distribuição assinada para Windows.
- Métricas locais de desempenho e consumo de recursos.
