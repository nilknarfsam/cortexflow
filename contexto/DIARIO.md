# Diário de evolução

Entradas mais recentes ficam no topo. Registre apenas trabalhos materiais.

## 2026-08-12 — Inicialização da Solução C# .NET 9 e Organização do Projeto

- Aprovada a migração para a nova arquitetura em **C# .NET 9 e WinUI 3**.
- Código Python original movido para `legacy_python/` via `git mv`, preservando histórico e os 63 testes unitários verdes.
- Criada a nova solução `CortexFlow.sln` com os projetos `CortexFlow.Core`, `CortexFlow.Infrastructure` e `CortexFlow.Core.Tests`.
- Instalados os pacotes NuGet `Whisper.net`, `Whisper.net.Runtime`, `CliWrap`, `PdfPig` e `DocumentFormat.OpenXml`.
- Implementado o `WhisperTranscriptionService` usando `Whisper.net` (`whisper.cpp`) com download de modelos GGML sob demanda.
- Implementado o `DocumentExtractorService` para leitura nativa de PDF, DOCX e TXT sem dependências externas.
- Implementado o `WindowsOcrService` preparado para OCR Nativo do Windows 10/11.
- Implementado o `MainViewModel` (MVVM) reativo integrado à fila assíncrona.
- **Reestruturação da Interface em 2 Abas Principais (Estúdio Integrado):**
  - **Aba 1 (`🎬 1. Conversão & Fila`):** Fila principal com DataGrid (85%), barra de ferramentas e rodapé de presets.
  - **Aba 2 (`👁️ 2. Visualizador & Player Sincronizado`):** Tela dividida integrada com visualização de texto transcrito, timestamps com botão `▶ Pular p/ Ponto` e Player MediaElement Direct3D.
  - O clique no botão **`👁️ Ver no Player`** em qualquer item da Fila (Aba 1) alterna automaticamente para a Aba 2 e carrega a mídia e o texto instantaneamente sem abrir janelas modais separadas!
- **Implementado Player de Mídia Sincronizado com Timestamps (`MainWindow.xaml`):**
  - Integração nativa do `MediaElement` (Windows Media Foundation).
- 16 testes automatizados xUnit aprovados em 80ms.


- **Corrigida a Estilização XAML da Menu Bar:** Adicionado estilo de `MenuItem` (`Background="#1E293B"`, `Foreground="#F8FAFC"`, highlight `#0EA5E9`), tornando os submenus (`Arquivo`, `Ferramentas`, `Exibir`, `Ajuda`) 100% legíveis e contrastantes no modo escuro.
- **Remoção Completa do Código Legado Python:** Removida a pasta `legacy_python/` (código totalmente extraído e substituído por C# .NET 9).
- **Atualização do GitHub Actions CI/CD:** `.github/workflows/quality.yml` simplificado para executar 100% em .NET 9 SDK (Restore, Release Build, xUnit).
- 15 testes xUnit aprovados e solução .NET 9 compilando 100% verde em modo Release.





- Criado o guia reutilizável `docs/GUIAMAESTRO_AVALIACAO_TECNOLOGICA.md` para avaliação de stack em futuros projetos.
- Registrada a decisão DEC-003.
- Próximo passo: Integrar o pacote `Whisper.net` no `CortexFlow.Infrastructure` para a prova de conceito de transcrição.


## 2026-07-29 — Subprocessos e build Windows validados

- Patch Windows isolado em módulo idempotente, preservando configurações explícitas
  e coberto por cinco testes de regressão.
- Executável ganhou `--smoke-test`, que valida imports e binários sem abrir a GUI.
- Build real aprovado com PyInstaller 6.21.0, FFmpeg e FFprobe 8.1.1; artefato
  one-directory com aproximadamente 816 MB.
- GUI do executável abriu como `CortexFlow 3.0.4`, permaneceu responsiva e aceitou
  encerramento normal.
- Suíte ampliada de 57 para 63 testes; cobertura do núcleo em 62%; lint e
  compilação aprovados.
- Próximo passo: iniciar refatoração incremental pelo `JobProcessor`.

## 2026-07-28 — Documentação pública profissional

- README reorganizado com posicionamento do produto, recursos confirmados,
  instalação Windows, diagnóstico, qualidade, arquitetura e privacidade.
- Limitações atuais, download inicial do modelo Whisper e ausência de licença
  foram documentados sem promessas além do que o código e os testes sustentam.
- Próximo passo: revisar subprocessos e adicionar smoke test do build one-directory.

## 2026-07-28 — Diagnóstico seguro integrado à interface

- Serviço: criado diagnóstico de FFmpeg, FFprobe, Tesseract, Whisper, PyTorch,
  modelo base, Python, sistema e escrita na pasta de dados.
- Privacidade: texto copiável não inclui caminhos locais, documentos ou
  credenciais.
- Interface: controles de executar e copiar adicionados às configurações
  avançadas; GUI abriu responsiva após a integração.
- Ambiente atual: FFmpeg/FFprobe/Whisper/PyTorch OK; Tesseract opcional ausente;
  modelo base será baixado no primeiro uso.
- Testes: suíte ampliada de 50 para 57; cobertura do núcleo em 61%; Ruff e
  `compileall` aprovados.
- Próximo passo: caracterizar subprocessos e build Windows.

## 2026-07-28 — Tooling e CI configurados

- Tooling: adicionados `pyproject.toml`, Ruff 0.16.0, coverage 7.15.2 e
  `requirements-dev.txt`.
- Baseline: 22 problemas objetivos de imports, variáveis e sombreamento corrigidos
  manualmente; import tardio necessário de `app.py` documentado como exceção.
- Cobertura: núcleo (`src/core`, `src/cache`, `src/models`) em 60%, com piso de
  CI em 55%; cobertura global medida em 21% e mantida como dívida explícita.
- CI: workflow Windows/Python 3.12 com dependências, lint, smoke de imports,
  testes, cobertura e `compileall`.
- Reprodutibilidade: dependências diretas fixadas nas versões usadas para abrir a
  GUI com sucesso.
- Validação local: 50 testes, Ruff, cobertura e compilação aprovados.
- Próximo passo: serviço de diagnóstico do ambiente.

## 2026-07-28 — Rede de segurança do núcleo concluída

- JobProcessor: adicionados testes para documento novo, cache reutilizado,
  cancelamento e erro de extração, todos com serviços falsos.
- Correção: cancelamento após extração agora notifica a UI e persiste o estado
  final em ambos os pontos de interrupção do pipeline.
- Testes: suíte ampliada de 46 para 50 testes, todos aprovados; `compileall`
  aprovado.
- Etapa: rede de segurança do núcleo concluída.
- Próximo passo: iniciar tooling e integração contínua.

## 2026-07-28 — Ambiente local e GUI validados

- Ambiente: criado `.venv` com Python 3.12 e instaladas as dependências de
  `requirements.txt`.
- Execução: `app.py` iniciado pelo ambiente virtual; janela `CortexFlow 3.0.4`
  abriu e permaneceu responsiva.
- Log: inicialização registrada sem erro em `data/logs/app.log`.
- Estado: aplicação deixada aberta para inspeção manual do usuário.

## 2026-07-28 — FFmpeg local, cache e fila cobertos

- Ambiente: FFmpeg e FFprobe 8.1.1 já estavam instalados via WinGet; ambos foram
  copiados para `bin/` e validados diretamente.
- Correção: `copy_local_binaries.ps1` agora aceita destino de teste, resolve os
  links do WinGet, procura os executáveis reais como fallback e valida o destino.
- Cache: adicionados testes de miss, hit, partial, configuração incompatível,
  registry/chunks corrompidos, round-trip de chunks e limpeza.
- Fila: adicionados testes de adição, validação, seleção, remoção, execução e
  recuperação; corrigida falha com contadores de sessão corrompidos.
- Testes: suíte ampliada de 31 para 46 testes, todos aprovados; `compileall`
  aprovado.
- Próximo passo: cobrir `JobProcessor` com serviços falsos.

## 2026-07-28 — Persistência, exportação e erros cobertos

- Resultado: concluídos os cenários adicionais de persistência; adicionados testes
  para exportação raw e classificação de erros.
- Cobertura funcional: JSON truncado, entradas inválidas, settings, histórico,
  registro de cache, TXT, Markdown, JSON, caminhos de saída e códigos de erro.
- Testes: suíte ampliada de 17 para 31 testes, todos aprovados; `compileall`
  aprovado.
- Código de produção: nenhuma mudança adicional foi necessária neste lote.
- Próximo passo: cobrir `CacheEngine` e depois `QueueManager` usando temporários e
  fakes.

## 2026-07-28 — Primeira correção segura de persistência

- Resultado: criada escrita JSON atômica e aplicada à fila, settings, histórico e
  registro de cache; recuperação normaliza progresso inválido ou fora da faixa e
  preserva metadados de dataset.
- Documentação: README alinhado ao repositório real e Python 3.12 definido como
  alvo oficial inicial; mensagens para instalador inexistente foram removidas.
- Testes: suíte ampliada de 12 para 17 testes, todos aprovados; `compileall`
  aprovado.
- Compatibilidade: regras de negócio e formatos JSON existentes foram preservados.
- Próximo passo: completar testes de persistência e iniciar cobertura de exportação
  e classificação de erros.

## 2026-07-28 — Plano de execução das melhorias

- Resultado: diagnóstico convertido em sete etapas ordenadas, da consolidação da
  linha de base à refatoração incremental.
- Evidências: 12 testes atuais aprovados; ausência de CI e configuração central;
  persistência direta de settings, histórico e cache; restauração de progresso sem
  tolerância a tipos inválidos.
- Decisão operacional: proteger persistência e criar testes antes de refatorar os
  componentes centrais.
- Próximo passo: executar a Etapa 0 e o primeiro bloco da Etapa 1.

## 2026-07-28 — Estrutura de memória do projeto

- Resultado: criado `AGENTS.md` na raiz e a pasta `contexto/` com estado atual,
  roadmap, decisões e diário.
- Base utilizada: inspeção do checkout, estrutura do código, documentação existente
  e execução dos 12 testes automatizados.
- Validação: os 12 testes passaram com Python 3.12 e o código passou por
  `compileall` antes desta reorganização documental.
- Risco: baixo; mudança apenas documental.
- Próximo passo sugerido: corrigir o README e iniciar o Horizonte 1 do roadmap.
