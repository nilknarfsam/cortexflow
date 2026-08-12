# CortexFlow

> Aplicação desktop local nativa para transformar áudios, vídeos, documentos e imagens em conteúdo estruturado, pesquisável e pronto para alimentar fluxos de Inteligência Artificial.

[![.NET 9](https://img.shields.io/badge/.NET-9.0-512BD4?logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/)
[![Windows 10/11](https://img.shields.io/badge/Plataforma-Windows_10_|_11-0078D6?logo=windows&logoColor=white)](https://microsoft.com/windows)
[![WinUI 3](https://img.shields.io/badge/UI-WinUI_3-0078D4?logo=windows11&logoColor=white)](https://learn.microsoft.com/windows/apps/winui/winui3/)
[![Whisper.net](https://img.shields.io/badge/Whisper-Whisper.net-412991?logo=openai&logoColor=white)](https://github.com/sandrobaglietto/Whisper.net)
[![Licença MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-yellow.svg)](LICENSE)
[![Processamento local](https://img.shields.io/badge/processamento-local-2E8B57)](#privacidade)

CortexFlow combina transcrição de mídia com **`Whisper.net` (`whisper.cpp`)**, extração de documentos com **`Windows.Media.Ocr`** nativo, pré-processamento via FFmpeg, fila assíncrona concorrente e exportação estruturada em uma interface moderna estilo **Conversor de Mídia Studio (WPF / WinUI 3)** para Windows.

---

## 🎯 Propósito & Visão

O **CortexFlow** nasceu da necessidade real de transcrever e extrair conteúdo de **áudios, vídeos, documentos PDF e imagens** para alimentar IAs (como NotebookLM, RAGs, LLMs e sistemas de conhecimento) com **conteúdo autêntico e sólido fornecido diretamente pelo próprio usuário**.

O foco principal atual é entregar um **transcritor e extrator profissional de alta performance, 100% local e orientado à privacidade**.

---

## ⚡ Visão Geral & Recursos

- **Transcrição Local em C#:** Integração nativa com `Whisper.net` (`whisper.cpp`) acelerado por GPU (CUDA/DirectML) ou CPU, com tradução automática de idiomas (`.WithTranslate()`).
- **Pré-processador de Mídia FFmpeg:** Converte áudios e vídeos (`.mp4`, `.mp3`, `.mkv`) em WAV 16kHz mono automaticamente, eliminando erros de cabeçalho RIFF.
- **Interface Estilo Conversor de Mídia Studio:** DataGrid ocupando **85% da tela**, Menu Bar nativa (`Arquivo`, `Ferramentas`, `Exibir`, `Ajuda`), Main Toolbar, ações por linha e StatusBar dinâmica.
- **OCR Nativo do Windows:** Utiliza a API `Windows.Media.Ocr` embutida no Windows 10/11 (sem necessidade de instalar Tesseract externamente).
- **Fila Assíncrona Thread-Safe:** Construída sobre `System.Threading.Channels` e o padrão MVVM.
- **Cache Inteligente SHA-256:** Gravações atômicas em JSON para reprocessamento instantâneo.
- **Modos de Estruturação & Exportação:** Presets para Raw, Clean, AI Ready, NotebookLM e Study Mode nos formatos `.md`, `.txt`, `.json` e `.pdf`.

---

## 💻 Requisitos de Desenvolvimento

| Componente | Obrigatório | Finalidade |
|---|:---:|---|
| Windows 10 ou 11 | Sim | Sistema operacional alvo |
| **.NET 9 SDK** | Sim | Runtime e compilador principal |
| FFmpeg e FFprobe | Sim | Extração e conversão de áudio/vídeo |
| Visual Studio 2022 ou VS Code | Não | IDE recomendada para C# |

---

## 🚀 Como Testar e Executar (1-Clique sem IDE)

### 🌟 Opção 1: Instalador 1-Clique & Execução via Terminal (`setup_and_run.bat`) — **Recomendado**
Ao clonar o repositório pela primeira vez, execute o script **[`setup_and_run.bat`](setup_and_run.bat)**. Ele fará tudo automaticamente no seu terminal:
1. Verifica se o **.NET 9 SDK** e **FFmpeg** estão instalados (instruindo como instalar se faltar).
2. Restaura todas as dependências **NuGet** da solução.
3. Executa os **15 testes automatizados xUnit** para garantir a integridade.
4. Inicia a aplicação diretamente do código-fonte com `dotnet run` sem precisar compilar um `.exe` nem abrir uma IDE!

### ⚡ Opção 2: Atalho de Execução Rápida (`run_app.bat`)
Basta dar dois cliques no arquivo **[`run_app.bat`](run_app.bat)** na raiz do projeto! O script compilará a solução atualizada e abrirá o aplicativo desktop imediatamente.

### 💻 Opção 3: Comandos do Terminal
```powershell
# Restaurar dependências NuGet
dotnet restore

# Compilar a solução .NET 9 em Release
dotnet build --configuration Release

# Executar a suíte de testes xUnit (15 testes)
dotnet test

# Executar a aplicação desktop
dotnet run --project src/CortexFlow.UI/CortexFlow.UI.csproj
```

---

## 📂 Estrutura do Repositório

```text
CortexFlow/
├── CortexFlow.sln                    # Solução principal .NET 9
├── setup_and_run.bat                 # Script 1-Clique: Verifica SDK, restaura NuGet, roda testes e executa no terminal
├── run_app.bat                       # Atalho de execução rápida com recompilação automática
├── LICENSE                           # Licença MIT (Franklin Carvalho)
├── src/                              # Projetos C# da nova arquitetura
│   ├── CortexFlow.Core/              # Modelos, interfaces, ViewModels e regras de negócio
│   ├── CortexFlow.Infrastructure/    # Integrações com Whisper.net, FFMpeg, PdfPig e Windows OCR
│   └── CortexFlow.UI/                # Interface visual em WinUI 3 / WPF Studio (MVVM)
├── tests/                            # Testes automatizados em xUnit
│   └── CortexFlow.Core.Tests/        # Testes de unidade das regras de negócio e infraestrutura
├── contexto/                         # Documentação viva de arquitetura e decisões (DEC-003)
├── docs/                             # Guias e templates (inclui Guia Maestro de Avaliação)
└── legacy_python/                    # Protótipo legado em Python 3.12 (preservado)
```

---

## 📖 Documentação & Memória Técnica

- **[`contexto/ESTADO_ATUAL.md`](contexto/ESTADO_ATUAL.md)** — Fotografia técnica detalhada da migração.
- **[`contexto/ROADMAP.md`](contexto/ROADMAP.md)** — Visão dos Horizontes do projeto.
- **[`contexto/DECISOES.md`](contexto/DECISOES.md)** — Registro da decisão **DEC-003** (Migração para C# .NET 9 / WinUI 3).
- **[`docs/GUIAMAESTRO_AVALIACAO_TECNOLOGICA.md`](docs/GUIAMAESTRO_AVALIACAO_TECNOLOGICA.md)** — Guia reutilizável para avaliação tecnológica e escolha de stack em novos projetos.

---

## 📄 Licença

Este projeto está licenciado sob a **Licença MIT** - consulte o arquivo [`LICENSE`](LICENSE) para mais detalhes. Copyright (c) 2026 **Franklin Carvalho (nilknarfsam)**.

---

## 🔒 Privacidade

O CortexFlow foi projetado desde o primeiro dia com o princípio de **100% de processamento local**. Nenhum áudio, vídeo, documento transcrito ou chave é enviado para servidores externos. Todo o processamento de IA é realizado diretamente na GPU/CPU da sua máquina local.
