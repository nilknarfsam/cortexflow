# Relatorio Executivo para Franklin

Franklin, o CortexFlow ja tem uma base forte: ele nao e apenas um transcritor simples. Ele tem fila, cache, historico, exportacao em varios formatos, pipeline AI-ready, biblioteca local, grafo de conhecimento e ferramentas de estudo. A arquitetura esta organizada em modulos, mas o projeto cresceu bastante e agora precisa de estabilizacao antes de novas funcionalidades.

## O Que Deve Ser Feito Primeiro

O primeiro foco deve ser estabilizar ambiente e empacotamento.

Motivo: o workspace observado usa Python 3.14.4, enquanto o projeto se apresenta como Python 3.10+. Para Whisper, Torch e PyInstaller, isso e um risco alto. Antes de mexer em interface ou motor, o ideal e garantir que o build seja reproduzivel com Python 3.10, 3.11 ou 3.12 e que FFmpeg esteja validado.

Tarefa inicial recomendada:

1. Criar/usar ambiente Python compativel.
2. Validar imports de Whisper, Torch, CustomTkinter e tkinterdnd2.
3. Validar `ffmpeg.exe` e `ffprobe.exe`.
4. Gerar build `onedir`.
5. Testar um audio curto no executavel final.

## Principais Descobertas

- A arquitetura principal e boa: `MainWindow -> QueueManager -> JobProcessor -> Transcription/Extraction/Export`.
- O pipeline avancado e poderoso, mas aumenta muito a superficie de manutencao.
- `data/` contem estado real de uso: cache, historico, fila e logs. Isso precisa de cuidado para nao ir para Git.
- Existem arquivos de UI legados mantidos no codigo, mas fora da janela principal.
- README, `agent.md` e codigo real nao estao 100% alinhados.
- A documentacao cita arquivos que nao existem na raiz atual: `CHANGELOG.md`, `instalar_dependencias.bat`, `app_transcricao.py`.
- A ausencia de testes para fila/cache/export/build deixa o projeto vulneravel a regressao.

## Riscos Encontrados

Alta prioridade:

- Build com Python 3.14.4.
- Falha de transcricao por FFmpeg/Whisper em executavel empacotado.
- Antivirus/SmartScreen bloqueando executavel ou subprocessos.
- Dados locais em `data/` entrando em commits.

Media prioridade:

- Pouca cobertura de testes.
- Paineis legados confundindo manutencao.
- Encoding/acentuacao corrompida em documentacao e strings observadas.
- Dependencia de Tesseract externa para OCR.

## O Que Nao Deve Ser Mexido Agora

- Nao remover `legacy_ui` ainda.
- Nao apagar `data/` sem decisao e backup.
- Nao refatorar `JobProcessor` agora.
- Nao trocar a UI principal agora.
- Nao adicionar novas features antes de fechar o build confiavel.
- Nao publicar release nem push antes de validar localmente.

## Proxima Tarefa Ideal para o Cursor

Pedir ao Cursor uma tarefa pequena e segura:

> "Atualize a documentacao de instalacao e build do CortexFlow para refletir o estado real do projeto, corrigindo referencias quebradas no README, documentando Python recomendado 3.10/3.11/3.12, FFmpeg em `bin/`, PyInstaller onedir e checklist de teste manual. Nao altere codigo funcional."

Essa e a melhor proxima tarefa porque reduz confusao, ajuda a resolver o problema de empacotamento e nao coloca o motor de transcricao em risco.
