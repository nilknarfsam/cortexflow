# Plano de execução

Criado em: 2026-07-28

Este plano transforma o roadmap em entregas pequenas, verificáveis e ordenadas por
dependência. Cada etapa deve terminar com testes, atualização da memória e um
checkout compreensível antes da próxima.

## Princípios

- Primeiro proteger dados e comportamento existente.
- Escrever o teste de regressão junto com cada correção.
- Não iniciar refatoração ampla sem uma rede mínima de testes.
- Separar mudanças de documentação, infraestrutura, correção e refatoração.
- Whisper, FFmpeg e GUI reais entram em testes de integração ou smoke tests; os
  testes unitários usam fakes e arquivos temporários.

## Etapa 0 — Consolidar a linha de base

Risco: baixo
Estimativa: uma entrega curta
Estado: concluída em 2026-07-28

### Trabalho

- Revisar e corrigir README: URL do repositório, comandos, arquivos inexistentes,
  versão suportada de Python e política de licença.
- Definir oficialmente Python 3.12 para desenvolvimento e build inicial.
- Documentar comandos de teste, execução e build realmente existentes.
- Preservar a memória criada em `AGENTS.md` e `contexto/`.

### Conclusão

- Uma instalação limpa pode seguir o README sem encontrar comandos inexistentes.
- Links locais do README apontam apenas para arquivos presentes.
- Testes atuais continuam aprovados.

## Etapa 1 — Proteger persistência e recuperação

Risco: baixo a médio
Estimativa: duas ou três entregas curtas
Estado: concluída em 2026-07-28

### Correções confirmadas

1. `PersistentQueue._dict_to_job()` converte `job_progress` com `float()` sem
   proteger `ValueError` ou `TypeError`. Um snapshot parcialmente corrompido pode
   interromper toda a recuperação em vez de descartar ou normalizar um item.
2. `SettingsService` grava settings e histórico diretamente no arquivo final.
3. `CacheRegistry` também grava diretamente no arquivo final e não trata falha de
   persistência.

Os três pontos foram corrigidos. A suíte cobre snapshots truncados, entradas
inválidas, preservação do arquivo anterior e integração com settings, histórico e
registro de cache.

### Trabalho

- Criar testes de JSON ausente, inválido, truncado e com campos de tipos errados.
- Normalizar progresso restaurado para o intervalo de 0 a 1.
- Criar uma função comum de escrita JSON atômica: arquivo temporário, flush,
  substituição e limpeza segura do temporário.
- Aplicar a escrita atômica em fila, settings, histórico e registro de cache.
- Padronizar logging e comportamento quando a escrita falhar.

### Conclusão

- Falhas de energia ou encerramento durante gravação não destroem o último estado
  válido.
- Um item corrompido não impede a recuperação dos demais.
- Testes não escrevem no diretório `data/` real.

## Etapa 2 — Rede de segurança do núcleo

Risco: baixo
Estimativa: três a cinco entregas
Estado: concluída em 2026-07-28

### Ordem dos testes

1. `ExportService`: raw, Markdown, JSON, nomes e diretórios de saída.
2. `job_errors`: arquivo, FFmpeg, permissão, memória, caminho longo e dependência.
3. `CacheEngine`: miss, partial, hit, mudança de configuração e cache inválido.
4. `QueueManager`: adicionar, duplicar, remover, iniciar, cancelar e finalizar.
5. `JobProcessor`: sucesso, cache, cancelamento e erro usando serviços falsos.

### Conclusão

- Núcleo exercitado sem baixar modelo Whisper.
- Cobertura medida e publicada no CI.
- Toda correção futura em fila, cache ou exportação exige teste de regressão.

## Etapa 3 — Tooling e integração contínua

Risco: baixo a médio
Estimativa: duas entregas
Estado: concluída em 2026-07-28

### Trabalho

- Criar `pyproject.toml` para Ruff, testes e cobertura.
- Definir limites de versões compatíveis em dependências.
- Separar dependências de runtime, desenvolvimento e build.
- Criar GitHub Actions para lint, testes e compilação em Python 3.12.
- Adicionar smoke test de imports que não inicialize a GUI nem baixe modelos.

### Conclusão

- Um pull request recebe resultado automático reproduzível.
- Ambiente local e CI executam os mesmos comandos.
- Dependências incompatíveis falham cedo e de forma compreensível.

## Etapa 4 — Diagnóstico do ambiente

Risco: médio
Estimativa: três entregas
Estado: concluída em 2026-07-28

### Trabalho

- Criar serviço sem UI para diagnosticar FFmpeg, FFprobe, Tesseract, Whisper,
  diretórios graváveis e versão do app.
- Exibir resumo na interface e permitir copiar diagnóstico seguro.
- Corrigir mensagens que ainda mencionam `instalar_dependencias.bat`.
- Cobrir classificação de erros com testes.
- Criar smoke test manual documentado usando mídia curta.

### Conclusão

- O usuário sabe qual dependência está ausente e como corrigir.
- O diagnóstico não expõe conteúdo de documentos nem credenciais.
- Suporte consegue reproduzir ambiente a partir do relatório.

## Etapa 5 — Subprocessos e build Windows

Risco: alto
Estimativa: duas a quatro entregas

### Trabalho

- Caracterizar com testes o patch global de `subprocess.Popen`.
- Verificar pipes, `stdin`, captura de erros, cancelamento e modo PyInstaller.
- Preferir uma fábrica/configuração localizada se os testes permitirem remover o
  monkey patch global.
- Automatizar validação do conteúdo de `dist/CortexFlow/`.
- Documentar origem e versão dos binários externos.

### Conclusão

- FFmpeg e Tesseract executam sem janelas indesejadas e sem perder stderr útil.
- Mudanças em subprocessos têm testes específicos no Windows.
- O build informa claramente binários ausentes.

## Etapa 6 — Refatoração incremental

Risco: médio a alto
Pré-requisito: etapas 1 a 3 concluídas

### Trabalho

- Extrair etapas do `JobProcessor` sem mudar resultados.
- Separar persistência, migração e preferências no `SettingsService`.
- Introduzir contratos para transcrição, extração, cache e exportação.
- Definir e executar a política para `src/ui/legacy_ui/`.
- Medir tempo de inicialização e uso de memória antes e depois.

### Conclusão

- Componentes podem ser testados isoladamente.
- Arquivos centrais diminuem de responsabilidade, não apenas de linhas.
- Cada extração mantém os testes anteriores verdes.

## Ciclo contínuo

Depois da base:

1. Selecionar um problema observável.
2. Registrar comportamento esperado.
3. Adicionar teste ou forma objetiva de validação.
4. Implementar a menor mudança suficiente.
5. Executar testes, lint e smoke test proporcional ao risco.
6. Atualizar estado, decisão e diário quando aplicável.
7. Revisar a prioridade do próximo item com base nos resultados.

## Próxima ação recomendada

Iniciar a Etapa 5 caracterizando com testes o patch global de subprocessos antes
de decidir se ele pode ser localizado ou deve permanecer global.
