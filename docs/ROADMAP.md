# Roadmap — Project Git Manager

Plano evolutivo em fases. A ordem preserva um produto utilizável em cada etapa.

## Fase 1 — Preservar app Python atual

- Estrutura de pastas híbrida (`legacy_python/`, `apps/`, `packages/`, `docs/`).
- Aplicação CustomTkinter em `legacy_python/customtkinter_app/`, executável pelos mesmos fluxos (com `cd` na pasta legada).
- Documentação de arquitetura e decisões na pasta `docs/`.

## Fase 2 — Extrair core Git

- Isolar a lógica Git em um módulo ou pacote Python claramente delimitado (importável sem UI).
- Reduzir acoplamento entre `ui/` e operações Git; facilitar testes unitários e futura duplicação/consumo por CLI ou host Node.

## Fase 3 — Criar CLI Python

- Interface de linha de comando (ex.: `python -m ...`) que exponha operações principais com saída estruturada (JSON), para integração futura com Electron sem acoplar à CustomTkinter.

## Fase 4 — Criar app Electron + React

- *Scaffold* Electron com `contextIsolation`, preload mínimo e renderer React + TypeScript.
- Telas iniciais: lista de projetos e feedback de operações; persistência local alinhada ao roadmap de SQLite.

## Fase 5 — Integrar Node com Python worker

- Definir contrato estável (versão de protocolo, mensagens, códigos de erro).
- Node orquestra `spawn` do Git e, quando necessário, subprocesso Python para automações e relatórios.

## Fase 6 — Build e release desktop

- Empacotamento para Windows (instalador ou artefato portátil), versionamento, logs e política de atualização.
- Documentação de instalação para usuário final e requisitos (Git no PATH, etc.).
