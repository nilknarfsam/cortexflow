# Roadmap

Última revisão: 2026-08-12

Execução detalhada: [`PLANO_EXECUCAO.md`](PLANO_EXECUCAO.md) e `contexto/ESTADO_ATUAL.md`.

## Visão

Evoluir o CortexFlow para um produto desktop profissional de alta performance em **C# / .NET 9 (WinUI 3 / WPF Fluent)**, garantindo processamento 100% offline, tamanho de instalador reduzido (200MB) e interface de conversão, transcrição e estudo de mídias de nível Studio.

## Horizonte 1 — Base confiável (Concluído)

- [Concluído] Corrigir instalação, links e comandos do README.
- [Concluído] Adotar `pyproject.toml` como configuração central.
- [Concluído] Configurar lint, formatação e cobertura.
- [Concluído] Criar CI para versões de Python oficialmente suportadas.
- [Concluído] Fixar ou limitar versões de dependências.
- [Concluído] Cobrir fila, persistência, cache, exportação e classificação de erros.

## Horizonte 2 — Runtime diagnosticável (Concluído)

- [Concluído] Diagnosticar FFmpeg, FFprobe, Tesseract, Python e modelo Whisper.
- [Concluído] Exibir mensagens acionáveis e opção de copiar diagnóstico.
- [Concluído] Padronizar logs sem expor conteúdo sensível.
- [Concluído] Criar smoke test do build.

## Horizonte 3 — Nova Arquitetura C# / .NET 9 (Concluído)

- [Concluído] Criar solução C# .NET 9 (`CortexFlow.sln`) com arquitetura limpa desacoplada (`Core`, `Infrastructure`, `UI`, `Core.Tests`).
- [Concluído] Pré-processamento FFmpeg automático para converter qualquer vídeo/áudio (`.mp4`, `.mp3`, `.mkv`) em WAV 16kHz mono (`AudioPreProcessor.cs`).
- [Concluído] Suporte a exportação multi-formato (`.md`, `.txt`, `.json`, `.pdf`), salvamento na pasta de origem ou customizada.
- [Concluído] Tradução automática de idiomas (`.WithTranslate()`) via `Whisper.net`.
- [Concluído] Formatação da transcrição em **Blocos de Tempo (30s)** e parágrafos legíveis.
- [Concluído] Manual do Usuário interativo em XAML (`HelpWindow.xaml` acessível via `F1`).
- [Concluído] Remoção completa do código legado Python e pipeline GitHub Actions 100% em .NET 9.

## Horizonte 4 — Próximas Evoluções Estratégicas (Em Planejamento)

### 🎨 Dimensão 1: UI/UX & Interatividade Visual
- [ ] **Player de Áudio/Vídeo Sincronizado:** Mini-player integrado na `ResultWindow.xaml` onde clicar em um timestamp `⏱️ [02:15]` pula o áudio/vídeo para o ponto exato.
- [ ] **Diarização de Locutores:** Identificação automática de quem falou (`Locutor 1:`, `Locutor 2:`) em podcasts e entrevistas.
- [ ] **Visualizador de Grafo Interativo:** Árvore gráfica de conceitos e nós semânticos com zoom e arraste.

### ⚡ Dimensão 2: Hardware Acceleration & Engine
- [ ] **Monitor de GPU em Tempo Real:** Leitura dinâmica de VRAM (NVIDIA CUDA / AMD DirectML) exibida na StatusBar.
- [ ] **Gerenciador de Modelos Whisper:** Aba para visualizar, baixar e excluir arquivos `.bin` de modelos (`tiny` a `large-v3`).

### 🧠 Dimensão 3: Inteligência Acadêmica & Integração IA Local
- [ ] **Exportação para Anki (`.apkg` / `.csv`):** Exportação direta dos Flashcards para o aplicativo Anki.
- [ ] **Integração com Ollama Local (RAG 100% Offline):** Suporte opcional a modelos LLM rodando na máquina local para perguntas e respostas.

### 📦 Dimensão 4: Empacotamento & Distribuição Windows
- [ ] **Build Standalone Self-Contained:** Executável `win-x64` sem necessidade de instalar o .NET 9 SDK na máquina do cliente.
- [ ] **Instalador executável leve (`CortexFlow_Setup.exe`).**
