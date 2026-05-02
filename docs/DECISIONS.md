# Decisões arquiteturais — Project Git Manager

Registro conciso de decisões já tomadas ou em vigor para orientar contribuições e evolução.

## D1 — Manter Python atual como base funcional

- A UI CustomTkinter em `legacy_python/customtkinter_app/` permanece a referência até a stack Electron + React estar pronta para uso diário.
- Evita *big bang* e permite validar contratos e comportamento Git lado a lado com a nova arquitetura.

## D2 — Separar UI da lógica pesada

- Operações Git, persistência e integrações com SO não devem depender de widgets.
- Objetivo: trocar ou acrescentar superfícies (CLI, Electron) sem reescrever o núcleo de domínio.

## D3 — Evitar `shell=True`

- Processos externos (Git, editores, futuros workers) devem usar listas de argumentos e `cwd` explícitos onde aplicável.
- Reduz risco de injeção de comando e comportamento divergente no Windows.

## D4 — Manter comandos Git isolados

- Centralizar chamadas ao executável `git` em um módulo de serviço (como no legado: `git_service`).
- Facilita auditoria, testes com *fixtures* e eventual migração para outra camada (Node) mantendo o mesmo contrato lógico.

## D5 — Preservar compatibilidade Windows

- Prioridade de desenvolvimento e testes em Windows (PATH, `CREATE_NO_WINDOW` onde já usado no legado, caminhos com `Path`).
- Linux/macOS como expansão documentada, sem quebrar o fluxo principal.

## D6 — Preparar integração com Cursor, VS Code e Flutter

- Abrir IDEs via executáveis configuráveis ou convenções de PATH (`code`, `cursor`, etc.).
- Futuras tarefas de build (Flutter CLI, npm, Python) como jobs com timeout e diretório de trabalho validado, não como shell livre concatenado.
