# Roadmap — Project Git Manager

Plano evolutivo em fases. A ordem preserva um produto utilizável em cada etapa.

## Fase 1 — Preservar app Python atual

- Estrutura de pastas híbrida (`legacy_python/`, `apps/`, `packages/`, `docs/`).
- Aplicação CustomTkinter em `legacy_python/customtkinter_app/`, executável pelos mesmos fluxos (com `cd` na pasta legada).
- Documentação de arquitetura e decisões na pasta `docs/`.

## Fase 2 — Extrair core Git (**concluída**)

- Pacote `packages/core/project_git_core/` com `git/service.py`, `git/models.py`, `utils/process.py` (`run_process` sem `shell=True`).
- `legacy_python/customtkinter_app/core/git_service.py` permanece como **adaptador** para a UI CustomTkinter (mesmas assinaturas e tuplas de retorno).
- `main.py` do legado adiciona `packages/core` ao `sys.path` para importar o núcleo a partir da raiz do monorepo.
- Testes mínimos em `tests/test_core_imports.py`.

## Fase 3 — Criar CLI Python (**concluída**)

- Pacote `packages/cli/projectgit/`: subcomandos `status`, `sync`, `clone`, `pull`, `commit`, `overview` via `argparse`, usando apenas `project_git_core`.
- Execução: a partir de `packages/cli`, `python -m projectgit.main …` ou `python -m projectgit` (ver `packages/cli/README.md`).
- Saída legível no terminal (UTF-8 no stdio quando suportado); JSON estruturado pode ser adicionado depois para integração com Electron.

## Fase 4 — Core e CLI instaláveis via pip (**concluída**)

- `packages/core/pyproject.toml`: distribuição `project-git-core`, import `project_git_core`.
- `packages/cli/pyproject.toml`: distribuição `projectgit`, dependência `project-git-core`, console script `projectgit`.
- Instalação dev na raiz: `pip install -e packages/core` e `pip install -e packages/cli` (core primeiro).
- CLI: prioriza import instalado (`find_spec`); mantém fallback de `sys.path` para clone do repo sem `pip`.

## Fase 5 — Criar app Electron + React

- *Scaffold* Electron com `contextIsolation`, preload mínimo e renderer React + TypeScript.
- Telas iniciais: lista de projetos e feedback de operações; persistência local alinhada ao roadmap de SQLite.

## Fase 6 — Integrar Node com Python worker

- Definir contrato estável (versão de protocolo, mensagens, códigos de erro).
- Node orquestra `spawn` do Git e, quando necessário, subprocesso Python para automações e relatórios.

## Fase 7 — Build e release desktop

- Empacotamento para Windows (instalador ou artefato portátil), versionamento, logs e política de atualização.
- Documentação de instalação para usuário final e requisitos (Git no PATH, etc.).
