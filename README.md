# CortexFlow 4.0 — Transcritor & Estúdio Profissional Local

> Aplicação desktop de alta performance em **C# / .NET 9 (WinUI 3 & WPF Fluent)** para transformar áudios, vídeos, documentos e imagens em conteúdo estruturado, pesquisável e pronto para alimentar fluxos de Inteligência Artificial.

[![.NET 9](https://img.shields.io/badge/.NET-9.0-512BD4?logo=dotnet&logoColor=white)](https://dotnet.microsoft.com/)
[![Windows 10/11](https://img.shields.io/badge/Plataforma-Windows_10_|_11-0078D6?logo=windows&logoColor=white)](https://microsoft.com/windows)
[![WinUI 3](https://img.shields.io/badge/UI-WinUI_3_|_WPF_Fluent-0078D4?logo=windows11&logoColor=white)](https://learn.microsoft.com/windows/apps/winui/winui3/)
[![Whisper.net](https://img.shields.io/badge/Whisper-Whisper.net_C++-412991?logo=openai&logoColor=white)](https://github.com/sandrobaglietto/Whisper.net)
[![Ollama Local](https://img.shields.io/badge/IA_Local-Ollama_RAG_Offline-000000?logo=ollama&logoColor=white)](https://ollama.com)
[![Testes xUnit](https://img.shields.io/badge/Testes_xUnit-17_Passando-10B981?logo=xunit&logoColor=white)](#testes)
[![Licença MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-yellow.svg)](LICENSE)
[![Processamento 100% Local](https://img.shields.io/badge/Processamento-100%25_Local_&_Offline-2E8B57)](#privacidade)

---

## 🎯 Propósito & Visão Arquitetural

O **CortexFlow** nasceu da necessidade real de transcrever e extrair conteúdo de **áudios, vídeos, documentos PDF, DOCX e imagens** para alimentar IAs (como NotebookLM, RAGs, LLMs e bases de conhecimento) com **conteúdo autêntico e sólido fornecido diretamente pelo próprio usuário**.

Reconstruído do zero de um protótipo Python para **C# .NET 9**, o CortexFlow oferece uma experiência de nível **Studio**, 93% mais leve (~200MB), sem dependências pesadas de terceiros e **100% offline**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CORTEXFLOW 4.0 - ARQUITETURA EM 3 CAMADAS                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
       ┌───────────────────────────────┼───────────────────────────────┐
       ▼                               ▼                               ▼
┌──────────────┐               ┌──────────────┐               ┌──────────────┐
│  CortexFlow  │ ────────────> │  CortexFlow  │ ────────────> │  CortexFlow  │
│     .UI      │               │    .Core     │               │.Infrastructure│
│ (WPF/WinUI3) │               │(MVVM/Domain) │               │(Whisper/FFmpeg)
└──────────────┘               └──────────────┘               └──────────────┘
```

---

## ⚡ Recursos de Engenharia & Destaques

- **🎬 Arquitetura em 2 Abas Estúdio Integrado (`MainWindow.xaml`):**
  - **Aba 1 (Conversão & Fila):** DataGrid dominante (85% da tela), drag-and-drop de mídias/pastas, seleção de presets (`Clean`, `Time Blocks 30s`, `AI Ready`, `NotebookLM`, `Study Mode`), modelos Whisper (`tiny` a `large-v3`), idiomas, formatos (`.md`, `.txt`, `.json`, `.pdf`, `.csv`) e salvamento customizado.
  - **Aba 2 (Visualizador & Player Sincronizado):** Painel único sem janelas popup bloqueantes.
- **🎵 Player Interativo com Scrubbing Fluido:** Controle nativo de áudio/vídeo (`MediaElement` Direct3D) com suporte a arrastar a agulha de tempo (`PreviewMouseDown`/`PreviewMouseUp`) em qualquer instante da mídia.
- **⏱️ Sincronismo em Tempo Real & Salto por Clique Duplo:** Acompanhamento ativo destacando em azul a linha da transcrição conforme a mídia toca + salto imediato ao dar clique duplo em qualquer fala.
- **⏱️ Predefinição por Blocos de Tempo (30s):** Organização das transcrições em intervalos marcados `### ⏱️ [MM:SS - MM:SS]` e quebras de parágrafo legíveis.
- **🎴 Exportador para Anki Flashcards (`.csv`):** Gerador automático de cartões Pergunta/Resposta prontos para o aplicativo Anki com 1 clique.
- **🦙 Conexão Opcional com Ollama Local (RAG 100% Offline):** Conector HTTP com `http://localhost:11434` (timeout de 3s) para gerar resumos executivos com LLMs locais sem enviar dados à nuvem.
- **📊 Monitor de Recursos na StatusBar:** Atualização assíncrona a cada 3s com o modelo de acelerador, núcleos de CPU e consumo de memória RAM do aplicativo.
- **📖 Manual do Usuário em XAML (`HelpWindow.xaml` - F1):** Modal com 5 abas intuitivas (Início Rápido, Predefinições, Modelos Whisper, Atalhos, Privacidade & 5S).

---

## 💻 Requisitos de Sistema

| Componente | Obrigatório | Recomendado / Observações |
|---|:---:|---|
| Sistema Operacional | Sim | Windows 10 ou Windows 11 (64-bit) |
| **.NET 9 SDK** | Sim | Versão 9.0.305 ou superior |
| FFmpeg / FFprobe | Sim | Pré-processamento automático de mídias |
| Ollama (Opcional) | Não | Para resumos com LLMs locais (`http://localhost:11434`) |

---

## 🚀 Como Executar (1-Clique sem IDE)

### 🌟 Opção 1: Instalador 1-Clique & Execução no Terminal (`setup_and_run.bat`) — **Recomendado**
Ao clonar o repositório, execute o script **[`setup_and_run.bat`](setup_and_run.bat)** no terminal:
1. Checa a presença do **.NET 9 SDK** e **FFmpeg**.
2. Restaura todas as dependências **NuGet** da solução C#.
3. Executa os **17 testes automatizados xUnit** para garantir integridade total.
4. Inicia a aplicação diretamente do código-fonte com `dotnet run` no terminal.

### ⚡ Opção 2: Atalho de Execução Rápida (`run_app.bat`)
Basta dar dois cliques no arquivo **[`run_app.bat`](run_app.bat)**! O script executa o `dotnet run` limpando qualquer cache antigo e abrindo o aplicativo atualizado.

### 💻 Opção 3: Comandos do Terminal
```powershell
# Restaurar dependências NuGet
dotnet restore CortexFlow.sln

# Compilar a solução .NET 9 em Release
dotnet build CortexFlow.sln --configuration Release

# Executar a suíte de 17 testes xUnit
dotnet test CortexFlow.sln

# Executar a aplicação desktop
dotnet run --project src/CortexFlow.UI/CortexFlow.UI.csproj
```

---

## 🧪 Testes Automatizados & Qualidade de Código

A solução possui **100% de aprovação** na suíte de testes unitários xUnit em `tests/CortexFlow.Core.Tests`:

```text
Execução de Teste Bem-sucedida.
Total de testes: 17
     Aprovados: 17
Tempo total: 0.76 Segundos
```

---

## 📂 Estrutura do Repositório

```text
CortexFlow/
├── CortexFlow.sln                    # Solução principal .NET 9
├── setup_and_run.bat                 # Script 1-Clique: Verifica SDK, restaura NuGet, roda testes e executa no terminal
├── run_app.bat                       # Atalho de execução rápida com recompilação dinâmica
├── LICENSE                           # Licença MIT (Franklin Carvalho)
├── src/                              # Arquitetura modular C#
│   ├── CortexFlow.Core/              # Abstrações, modelos, ViewModels (MVVM) e regras de negócio
│   ├── CortexFlow.Infrastructure/    # Whisper.net, FFmpeg PreProcessor, OllamaService, PdfPig e Windows OCR
│   └── CortexFlow.UI/                # Interface visual WinUI 3 / WPF Estúdio em 2 Abas
├── tests/                            # Suíte de testes automatizados
│   └── CortexFlow.Core.Tests/        # Testes xUnit de unidade (17 testes verdes)
├── contexto/                         # Documentação viva de arquitetura, diário e decisões (DEC-003)
└── docs/                             # Relatórios de qualidade (5S, KPIs, Checklist de Evolução)
```

---

## 📖 Documentação & Relatórios Técnicos

- **[`contexto/ESTADO_ATUAL.md`](contexto/ESTADO_ATUAL.md)** — Fotografia técnica detalhada da arquitetura C#.
- **[`contexto/ROADMAP.md`](contexto/ROADMAP.md)** — Horizontes estratégicos do projeto.
- **[`docs/CHECKLIST_EVOLUCAO_CORTEXFLOW.md`](docs/CHECKLIST_EVOLUCAO_CORTEXFLOW.md)** — Checklist consolidado (O que foi feito, Antes x Depois, Próximas Evoluções).
- **[`docs/DESENVOLVIMENTO_5S_KPIS_SEGURANCA.md`](docs/DESENVOLVIMENTO_5S_KPIS_SEGURANCA.md)** — Diretrizes da metodologia 5S em software, KPIs de performance e matriz de riscos.

---

## 🔒 Privacidade & Segurança de Dados

O CortexFlow foi desenvolvido com o compromisso de **100% de processamento local**. Nenhum áudio, vídeo, documento transcrito ou dado pessoal é transmitido para a nuvem. Todo o processamento do Whisper.net e OCR é realizado diretamente na sua GPU/CPU local.

---

## 📄 Licença

Este projeto está licenciado sob a **Licença MIT** - consulte o arquivo [`LICENSE`](LICENSE) para mais detalhes. Copyright (c) 2026 **Franklin Carvalho (nilknarfsam)**.
