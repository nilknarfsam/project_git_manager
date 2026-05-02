# Project Git Manager

**Gerenciador Git de Projetos** — aplicação desktop para trabalhar com repositórios Git por interface gráfica (clone, status, pull, commit/push, favoritos e integração com VS Code).

Repositório: [github.com/nilknarfsam/project_git_manager](https://github.com/nilknarfsam/project_git_manager)

## Versão atual (legado)

A interface em uso hoje é **Python 3** + **CustomTkinter**. O código vive em `legacy_python/customtkinter_app/` e continua sendo a base funcional; nada foi removido, apenas reorganizado.

## Nova direção (arquitetura híbrida)

O projeto evolui para um *Dev Workflow Manager* com camadas separadas: **Electron** + **React** + **TypeScript** na UI desktop, **Node.js** no processo principal (IPC, processos, persistência), **Python** para automações e relatórios, **SQLite** para dados locais e **Git CLI** como dependência externa. Detalhes em [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), fases em [docs/ROADMAP.md](docs/ROADMAP.md) e decisões em [docs/DECISIONS.md](docs/DECISIONS.md).

## Objetivo

Simplificar tarefas do dia a dia com Git em qualquer pasta do computador: escolher o projeto, ver o status, atualizar do remoto, publicar alterações e manter uma lista de projetos favoritos, sem depender só da linha de comando.

## Stack (legado CustomTkinter)

| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3 |
| Interface | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) |
| Git | `subprocess` (sem `shell=True`), compatível com Windows (`CREATE_NO_WINDOW` onde aplicável) |
| Persistência | JSON (`legacy_python/customtkinter_app/data/projects.json`) |

## Funcionalidades atuais (legado)

- Seleção de pasta do projeto e campo de caminho editável
- Abrir pasta no **VS Code** (`code` no PATH)
- Salvar e carregar **projetos favoritos** (`data/projects.json` dentro do app legado)
- **Clonar** repositório (URL + caminho completo da pasta final)
- Se a pasta de destino **já existir** e for um repositório Git, **sincronização forçada** com o remoto (ver aviso abaixo)
- **Git status**, **pull**, **commit + push** (com mensagem), com validação de `.git`
- Console de log com destaque para sucesso e erro
- Operações Git em **thread** para não travar a janela

## Aviso importante — sincronização forçada

Quando a pasta de destino do clone **já existe** e contém um repositório Git válido, o aplicativo executa uma **sincronização forçada** em vez de um clone novo:

1. `git fetch origin`
2. `git reset --hard origin/<branch-atual>`
3. `git clean -fd`

Isso **descarta commits e alterações locais não enviadas** na branch atual e **remove arquivos não rastreados** (exceto ignorados pelo padrão do `git clean -fd`). Use apenas se tiver certeza de que pode perder trabalho local nessa pasta.

## Como executar a versão atual (Python + CustomTkinter)

```bash
cd legacy_python/customtkinter_app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

No Linux/macOS, ative o ambiente virtual com `source venv/bin/activate`.

Requisitos no sistema: **Git** no PATH; para “Abrir no VS Code”, o comando `code` no PATH.

## CLI (`projectgit`)

Linha de comando sobre o mesmo núcleo (`project_git_core`), sem CustomTkinter.

```bash
cd packages/cli
python -m projectgit.main overview "C:\src\meu-repo"
python -m projectgit.main status "C:\src\meu-repo"
python -m projectgit.main pull "C:\src\meu-repo"
python -m projectgit.main sync "C:\src\meu-repo"
python -m projectgit.main clone "https://github.com/org/repo.git" "C:\src\repo"
python -m projectgit.main commit "C:\src\meu-repo" -m "mensagem do commit"
```

Detalhes: [packages/cli/README.md](packages/cli/README.md).

## Estrutura do repositório

```
project_git_manager/
  README.md
  docs/
    ARCHITECTURE.md
    ROADMAP.md
    DECISIONS.md
  legacy_python/
    customtkinter_app/
      main.py
      requirements.txt
      ui/
      core/
      data/
  apps/
    desktop/          # reservado — Electron + React (futuro)
  packages/
    cli/              # CLI Python projectgit
    core/             # project_git_core — operações Git reutilizáveis
    python_worker/    # reservado — worker Python (futuro)
  data/               # reservado — persistência da nova stack (futuro)
```

## APIs principais (`legacy_python/customtkinter_app/core/`)

- **git_service**: `run_git_command`, `validate_git_repo`, `clone_repo`, `force_sync_repo`, `pull_repo`, `commit_and_push`, `get_status`, etc.
- **project_service**: `load_projects`, `save_project`, `get_projects`

## Autor

**Franklin** — [@nilknarfsam](https://github.com/nilknarfsam)

## Licença

Defina a licença desejada (por exemplo MIT) ao publicar o repositório.
