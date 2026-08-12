# CortexFlow

> Aplicação desktop local nativa para transformar áudios, vídeos, documentos e imagens em conteúdo estruturado, pesquisável e pronto para alimentar fluxos de Inteligência Artificial.

[![.NET 9](https://img.shields.io/badge/.NET-9.0-512BD4?logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/)
[![Windows 10/11](https://img.shields.io/badge/Plataforma-Windows_10_|_11-0078D6?logo=windows&logoColor=white)](https://microsoft.com/windows)
[![WinUI 3](https://img.shields.io/badge/UI-WinUI_3-0078D4?logo=windows11&logoColor=white)](https://learn.microsoft.com/windows/apps/winui/winui3/)
[![Whisper.net](https://img.shields.io/badge/Whisper-Whisper.net-412991?logo=openai&logoColor=white)](https://github.com/sandrobaglietto/Whisper.net)
[![Licença MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-yellow.svg)](LICENSE)
[![Processamento local](https://img.shields.io/badge/processamento-local-2E8B57)](#privacidade)

CortexFlow combina transcrição de mídia com **`Whisper.net` (`whisper.cpp`)**, extração de documentos com **`Windows.Media.Ocr`** nativo, fila assíncrona concorrente e exportação estruturada em uma interface moderna **WinUI 3 (Fluent Design)** para Windows.

---

## 🎯 Propósito & Visão

O **CortexFlow** nasceu da necessidade real de transcrever e extrair conteúdo de **áudios, vídeos, documentos PDF e imagens** para alimentar IAs (como NotebookLM, RAGs, LLMs e sistemas de conhecimento) com **conteúdo autêntico e sólido fornecido diretamente pelo próprio usuário**.

O foco principal atual é entregar um **transcritor e extrator profissional de alta performance, 100% local e orientado à privacidade**.

---

## ⚡ Visão Geral & Recursos

- **Transcrição Local em C#:** Integração nativa com `Whisper.net` (`whisper.cpp`) acelerado por GPU (CUDA/DirectML) ou CPU.
- **OCR Nativo do Windows:** Utiliza a API `Windows.Media.Ocr` embutida no Windows 10/11 (sem necessidade de instalar Tesseract externamente).
- **Interface Nativa WinUI 3:** Fluent Design com suporte a Drag-and-Drop, temas claros/escuros e alta responsividade.
- **Fila Assíncrona Thread-Safe:** Construída sobre `System.Threading.Channels` e o padrão MVVM com `CommunityToolkit.Mvvm`.
- **Cache Inteligente SHA-256:** Gravações atômicas em JSON para reprocessamento instantâneo.
- **Modos de Estruturação:** Raw, Clean, AI Ready, NotebookLM e Study Mode.

---

## 💻 Requisitos de Desenvolvimento

| Componente | Obrigatório | Finalidade |
|---|:---:|---|
| Windows 10 ou 11 | Sim | Sistema operacional alvo |
| **.NET 9 SDK** | Sim | Runtime e compilador principal |
| FFmpeg e FFprobe | Sim | Extração e conversão de áudio/vídeo |
| Visual Studio 2022 ou VS Code | Não | IDE recomendada para C# / WinUI 3 |

---

## 🚀 Como Compilar e Executar

Abra o terminal no repositório clonado:

```powershell
# Compilar a solução .NET 9
dotnet build

# Executar a suíte de testes xUnit
dotnet test
```

---

## 📂 Estrutura do Repositório

```text
CortexFlow/
├── CortexFlow.sln                    # Solução principal .NET 9
├── LICENSE                           # Licença MIT (Francklin Campos)
├── src/                              # Projetos C# da nova arquitetura
│   ├── CortexFlow.Core/              # Modelos, interfaces, ViewModels e regras de negócio
│   ├── CortexFlow.Infrastructure/    # Integrações com Whisper.net, FFMpeg, PdfPig e Windows OCR
│   └── CortexFlow.UI/                # Interface visual em WinUI 3 (MVVM)
├── tests/                            # Testes automatizados em xUnit
│   └── CortexFlow.Core.Tests/        # Testes de unidade das regras de negócio e infraestrutura
├── contexto/                         # Documentação viva de arquitetura e decisões (DEC-003)
├── docs/                             # Guias e templates (inclui Guia Maestro de Avaliação)
└── legacy_python/                    # Protótipo legado em Python 3.12 (preservado)
```

---

## 📖 Documentação & Memória Técnica

- **[`contexto/ESTADO_ATUAL.md`](contexto/ESTADO_ATUAL.md)** — Fotografia técnica detalhada da migração.
- **[`contexto/DECISOES.md`](contexto/DECISOES.md)** — Registro da decisão **DEC-003** (Migração para C# .NET 9 / WinUI 3).
- **[`docs/GUIAMAESTRO_AVALIACAO_TECNOLOGICA.md`](docs/GUIAMAESTRO_AVALIACAO_TECNOLOGICA.md)** — Guia reutilizável para avaliação tecnológica e escolha de stack em novos projetos.

---

## 📄 Licença

Este projeto está licenciado sob a **Licença MIT** - consulte o arquivo [`LICENSE`](LICENSE) para mais detalhes. Copyright (c) 2026 **Francklin Campos (nilknarfsam)**.

---

## 🔒 Privacidade

O CortexFlow foi desenvolvido para processar todo o conteúdo localmente no computador do usuário. Suas transcrições, arquivos, dados de cache e históricos nunca são enviados para servidores externos ou APIs pagas na nuvem.
