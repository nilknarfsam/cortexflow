# 📋 Guia Maestro de Avaliação Tecnológica & Escolha de Stack

> **Instruções de Uso:** Utilize este documento como instrução/prompt de entrada para qualquer Inteligência Artificial (Gemini, Claude, GPT, DeepSeek, etc.) antes de iniciar o desenvolvimento de um novo projeto. O objetivo é evitar criar protótipos em tecnologias inviáveis para o produto final.

---

## 🎯 Prompt Inicial para a IA

> *"Atue como um Arquiteto de Software Principal. Estou iniciando um novo projeto e preciso que você avalie as melhores tecnologias, frameworks, linguagens e arquiteturas para construir esta solução. Analise as opções sob a ótica de **Protótipo Rápido vs. Produto Final Escalável/Comercial**."*

---

## 🔍 Informações do Projeto (Preencha antes de enviar)

1. **Descrição da Ideia:**
   - [Descreva em poucas frases o que o sistema/aplicativo fará]

2. **Plataforma Alvo Principal:**
   - [ ] Desktop (Windows, macOS, Linux)
   - [ ] Web (SaaS / Navegador)
   - [ ] Mobile (iOS, Android)
   - [ ] CLI / Backend / API
   - [ ] Multiplataforma

3. **Requisitos de Performance & Recursos:**
   - **Processamento:** [ ] Local (Offline/No-Device) | [ ] Nuvem (Cloud APIs) | [ ] Híbrido
   - **Tamanho do Executável/App:** Exigência de app leve? [ ] Sim | [ ] Não crítico
   - **Carga de Dados/Mídia:** Transcrição de áudio, visão computacional, arquivos pesados, etc.

4. **Objetivo Atual:**
   - [ ] **Fase 1 (MVP/Protótipo):** Validar a ideia no menor tempo possível (1 a 2 semanas).
   - [ ] **Fase 2 (Produto Final/Produção):** Criar uma aplicação comercial estável, leve, segura e de alta performance.

---

## 📊 Critérios de Avaliação Obrigatórios que a IA Deve Responder

Solicite que a IA analise o projeto cruzando as seguintes opções de tecnologias com a tabela de critérios abaixo:

### Matriz de Decisão por Categoria

| Categoria | Opção A (Linguagem/Framework) | Opção B (Linguagem/Framework) | Opção C (Linguagem/Framework) |
|---|---|---|---|
| **Facilidade de Prototipagem** | (Ex: Python/CustomTkinter) | (Ex: C#/.NET 8 WinUI 3) | (Ex: Electron/Tauri + React) |
| **Desempenho & Concorrência** | | | |
| **Tamanho do Artefato/Instalador** | | | |
| **Consumo de RAM/CPU** | | | |
| **Experiência Visual (UI/UX)** | | | |
| **Segurança e Propriedade Intelectual** | | | |
| **Custo de Manutenção em Longo Prazo** | | | |

---

## 💡 Regras de Ouro para Tomada de Decisão Tecnológica

### Quando Escolher Python:
- **Recomendado para:** Scripts, automações backend, data science, treinamento de modelos de IA, microsserviços na nuvem, protótipos de validação rápida.
- **Evitar para:** Aplicações desktop comerciais pesadas que exigem instalador leve, UI responsiva nativa e proteção contra engenharia reversa do código-fonte.

### Quando Escolher C# (.NET 8/9):
- **Recomendado para:** Aplicações desktop corporativas/comerciais para Windows (WPF/WinUI 3) ou multiplataforma (Avalonia/MAUI), sistemas de alta performance, software local com multithreading pesado.
- **Vantagens:** Compilação nativa (AOT/Self-contained), consumo baixo de memória, instaladores pequenos, ecossistema gigante e integração nativa com o Windows.

### Quando Escolher Rust / C++:
- **Recomendado para:** Motores de mídia, processamento de baixo nível, jogos, componentes onde cada milissegundo de CPU conta.

### Quando Escolher TypeScript / Tauri / Electron:
- **Recomendado para:** Interfaces web ricas reutilizadas no desktop. **Preferir Tauri sobre Electron** para manter o instalador leve (Tauri usa Rust no backend e WRY no frontend, gerando apps de 15MB).

---

## 🚀 Pergunta Final para a IA Responder

> *"Com base nos dados acima, apresente um **Veredito Técnico**: devemos começar direto no stack de produção ou fazer um protótipo rápido primeiro? Qual a arquitetura recomendada para que o protótipo possa evoluir para produção sem precisar ser jogado fora?"*
