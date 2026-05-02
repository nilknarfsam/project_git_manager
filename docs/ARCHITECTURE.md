# Arquitetura — Project Git Manager

Este documento descreve a **visão híbrida** do projeto após a reorganização do repositório. A implementação completa ocorrerá em fases; consulte [ROADMAP.md](ROADMAP.md).

## Visão geral

O **Project Git Manager** evolui para um *Dev Workflow Manager* com camadas separadas:

1. **Interface (futura)** — experiência desktop moderna, desacoplada da lógica pesada.
2. **Host desktop (futuro)** — empacotamento, janelas, menu e políticas de segurança no processo principal.
3. **Orquestração local (futura)** — integração com sistema operacional, processos, IPC e persistência.
4. **Automações (Python)** — relatórios, scripts técnicos e tarefas que se beneficiam do ecossistema Python.
5. **Persistência local** — metadados, histórico de operações e configurações em banco relacional leve.

A versão **legada** em Python + CustomTkinter permanece funcional em `legacy_python/customtkinter_app/` até a nova stack atingir paridade.

## Stack por responsabilidade

| Responsabilidade | Tecnologia planejada |
|------------------|----------------------|
| UI rica e componentizada | **React** + **TypeScript** |
| Shell desktop (Windows prioritário) | **Electron** |
| IPC, spawn de processos, FS, SQLite no desktop | **Node.js** (processo principal Electron) |
| Automação, relatórios, pipelines de arquivo | **Python** (*worker* / subprocesso) |
| Estado local, histórico, filas | **SQLite** |
| Operações de repositório | **Git CLI** (dependência externa; invocação com argumentos explícitos, sem `shell=True`) |

## Comunicação entre módulos (futuro)

Fluxo alvo:

```
Renderer (React)  →  preload (API mínima)  →  Main (Node)
                                                    ↓
                              ┌─────────────────────┼─────────────────────┐
                              ↓                     ↓                     ↓
                         Git (spawn)           SQLite                Python worker
                         argv[], cwd           (metadados)           (JSON stdin/stdout)
```

- A UI envia **comandos tipados** (ex.: status, pull) e identificadores estáveis; não monta strings de shell com dados do usuário.
- O processo principal **valida** caminhos e resolve `projectId` → diretório permitido antes de qualquer `spawn`.
- O **worker Python** (quando existir) recebe payloads estruturados (JSON) e devolve resultados estruturados, para manter contratos claros e testáveis.

## Pacotes no repositório

- `legacy_python/customtkinter_app/` — aplicação atual (referência e base funcional).
- `apps/desktop/` — futura aplicação Electron + React.
- `packages/core/project_git_core/` — **núcleo Git reutilizável** (Python): subprocess seguro, modelos (`GitCommandResult`, `RepositoryOverview`) e serviço Git sem dependência de UI. Instalável como `pip install -e packages/core` (distribuição `project-git-core`).
- `packages/cli/projectgit/` — **CLI** (`projectgit`): subcomandos `argparse` que chamam apenas o core; instalável como `pip install -e packages/cli` (comando `projectgit`). Fallback de `sys.path` se o core não estiver instalado.
- `legacy_python/customtkinter_app/core/git_service.py` — **adaptador de compatibilidade**: expõe as mesmas funções e tuplas que a UI CustomTkinter já usava, delegando para `project_git_core`. A UI não deve usar `subprocess` diretamente para Git.
- `packages/python_worker/` — futuro pacote ou entrypoint do worker Python.
- `data/` na raiz — reservado para dados da nova stack (ex.: SQLite) em fases futuras; não confundir com `legacy_python/customtkinter_app/data/` (JSON da UI legada).

### Direção para novas UIs

- Preferir importar e chamar **`project_git_core`** (ou um backend que o encapsule) em vez de duplicar chamadas a `git`.
- O processo Electron/Node futuro pode orquestrar o mesmo núcleo via subprocesso Python ou reimplementar apenas a orquestração, mantendo contratos alinhados aos tipos do core.

## Referências

- [ROADMAP.md](ROADMAP.md) — fases de implementação.
- [DECISIONS.md](DECISIONS.md) — decisões arquiteturais registradas.
