# CortexFlow

> Aplicação desktop local nativa para transformar áudios, vídeos e documentos em conteúdo estruturado, pesquisável e pronto para fluxos de conhecimento.

[![.NET 9](https://img.shields.io/badge/.NET-9.0-512BD4?logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/)
[![Windows 10/11](https://img.shields.io/badge/Plataforma-Windows_10_|_11-0078D6?logo=windows&logoColor=white)](https://microsoft.com/windows)
[![WinUI 3](https://img.shields.io/badge/UI-WinUI_3-0078D4?logo=windows11&logoColor=white)](https://learn.microsoft.com/windows/apps/winui/winui3/)
[![Whisper.net](https://img.shields.io/badge/Whisper-Whisper.net-412991?logo=openai&logoColor=white)](https://github.com/sandrobaglietto/Whisper.net)
[![Processamento local](https://img.shields.io/badge/processamento-local-2E8B57)](#privacidade)

CortexFlow combina transcrição de mídia com **`Whisper.net` (`whisper.cpp`)**, extração de documentos com **`Windows.Media.Ocr`** nativo, fila assíncrona concorrente e exportação estruturada em uma interface moderna **WinUI 3 (Fluent Design)** para Windows.

O projeto está em transição de arquitetura de um protótipo inicial em Python para uma aplicação desktop nativa em **C# / .NET 9**, garantindo **desempenho ultra-rápido, consumo reduzido de RAM e um executável leve de ~200 MB**.

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
├── src/                              # Projetos C# da nova arquitetura
│   ├── CortexFlow.Core/              # Modelos, interfaces e regras de negócio
│   ├── CortexFlow.Infrastructure/    # Integrações com Whisper.net, FFMpeg e Windows OCR
│   └── CortexFlow.UI/                # Interface visual em WinUI 3 (MVVM)
├── tests/                            # Testes automatizados em xUnit
│   └── CortexFlow.Core.Tests/        # Testes de unidade das regras de negócio C#
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

## 🔒 Privacidade

O CortexFlow foi desenvolvido para processar todo o conteúdo localmente no computador do usuário. Suas transcrições, arquivos, dados de cache e históricos nunca são enviados para servidores externos ou APIs pagas na nuvem.
