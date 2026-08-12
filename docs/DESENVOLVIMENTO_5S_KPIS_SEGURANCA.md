# Diretrizes de Qualidade, Metodologia 5S, KPIs e Segurança de Dados — CortexFlow 4.0

Este documento estabelece o guia prático de arquitetura, boas práticas, aplicação da filosofia **5S em Software**, definição de **KPIs de Qualidade** e diretrizes de **Segurança de Dados** para a nova base em **C# .NET 9 (WinUI 3 / WPF)**.

---

## 🍃 1. Aplicação da Filosofia 5S no Desenvolvimento de Software

A metodologia 5S tradicional foi adaptada para a engenharia de software do CortexFlow:

| Senso 5S | Conceito em Software | Prática no CortexFlow 4.0 |
|---|---|---|
| **1. Seiri (Senso de Utilização)** | Eliminação de código morto, arquivos não utilizados e dependências desnecessárias | Remoção total da pasta `legacy_python/`, limpeza de bibliotecas não utilizadas e foco 100% no SDK do .NET 9. |
| **2. Seiton (Senso de Organização)** | Arquitetura limpa com separação clara de responsabilidades | Estrutura modular em 3 camadas: `CortexFlow.Core` (Regras/Modelos), `CortexFlow.Infrastructure` (Motores/APIs), `CortexFlow.UI` (WPF/WinUI 3). |
| **3. Seiso (Senso de Limpeza)** | Limpeza de arquivos temporários, sanitização de logs e cache | Exclusão automática de buffers de áudio WAV 16kHz pós-transcrição, opção de limpar cache SHA-256 e sanitização de logs. |
| **4. Seiketsu (Senso de Padronização)** | Padrões de código, contratos de interface e MVVM | Padrão MVVM com `CommunityToolkit.Mvvm`, contratos rígidos (`ITranscriptionService`, `ICacheService`, `IExportService`, `IQueueManager`). |
| **5. Shitsuke (Senso de Disciplina)** | Automação de testes e barreira de qualidade contínua | Suíte de testes automatizados `xUnit` executados a cada build e pipeline estrito no GitHub Actions CI/CD (`quality.yml`). |

---

## 📊 2. KPIs (Key Performance Indicators) de Qualidade de Software

Para manter a qualidade e o desempenho do CortexFlow em nível profissional, acompanhamos os seguintes indicadores:

### A. Desempenho e Performance
- **Proporção de Transcrição (RTF - Real Time Factor):**
  - Alvo por GPU (NVIDIA CUDA / DirectML): $\le 0.15 \times$ do tempo real (transcrever 10 min em < 1.5 min).
  - Alvo por CPU: $\le 0.50 \times$ do tempo real.
- **Consumo de Memória RAM:** $\le 350 \text{ MB}$ em idle, $\le 1.2 \text{ GB}$ durante o carregamento de modelos `base`/`small`.
- **Tamanho do Instalador/Build:** $\le 200 \text{ MB}$ (redução de 93% comparado aos 3 GB do protótipo PyTorch).

### B. Confiabilidade e Estabilidade
- **Taxa de Sucesso da Fila:** $100\%$ de conclusão sem travamento ou vazamento de `IDisposable`.
- **Cobertura de Testes Automatizados:** Manter $100\%$ de aprovação na suíte de testes xUnit (15 testes passando em < 100ms).
- **Compilação Limpa:** Zero erros e zero avisos de compilação em modo `Release`.

---

## 🔒 3. Privacidade e Segurança de Dados

O CortexFlow lida com conteúdos sensíveis (aulas, reuniões, gravações pessoais e livros). Por isso, cumpre rigorosamente os seguintes pilares:

1. **100% Offline & Processamento Local:**
   - Todo o áudio, vídeo, documento PDF/DOCX ou imagem permanece estritamente na máquina do usuário.
   - O modelo `Whisper.net` executa via código nativo C++ (`whisper.cpp`) dentro da memória da aplicação.
2. **Zero Telemetria Externa:**
   - Nenhuma métrica, IP ou arquivo é enviado para servidores remotos ou APIs de terceiros.
3. **Sanitização de Caminhos e Credenciais:**
   - O sistema não registra nomes de usuários do Windows nem credenciais privadas nos relatórios de logs.
4. **Isolamento do Cache:**
   - O cache SHA-256 é armazenado criptograficamente por hash de conteúdo no diretório `AppData/Local/CortexFlow`, podendo ser limpo a qualquer momento com 1 clique.
