# Project Git Manager

**Gerenciador Git de Projetos** — aplicação desktop em Python para trabalhar com repositórios Git por interface gráfica (clone, status, pull, commit/push, favoritos e integração com VS Code).

## Objetivo

Simplificar tarefas do dia a dia com Git em qualquer pasta do computador: escolher o projeto, ver o status, atualizar do remoto, publicar alterações e manter uma lista de projetos favoritos, sem depender só da linha de comando.

## Stack

| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3 |
| Interface | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) |
| Git | `subprocess` (sem `shell=True`), compatível com Windows (`CREATE_NO_WINDOW` onde aplicável) |
| Persistência | JSON (`data/projects.json`) |

## Funcionalidades atuais

- Seleção de pasta do projeto e campo de caminho editável
- Abrir pasta no **VS Code** (`code` no PATH)
- Salvar e carregar **projetos favoritos** (`data/projects.json`)
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

## Instalação

```bash
cd project_git_manager
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

No Linux/macOS, ative o ambiente virtual com `source venv/bin/activate`.

## Execução

Na raiz do repositório (pasta que contém `main.py` e `data/`):

```bash
python main.py
```

Requisitos no sistema: **Git** no PATH; para “Abrir no VS Code”, o comando `code` no PATH.

## Estrutura do repositório

```
project_git_manager/
  main.py
  ui/
    main_window.py
    components.py
  core/
    git_service.py
    project_service.py
  data/
    projects.json
  requirements.txt
  README.md
```

## APIs principais (`core/`)

- **git_service**: `run_git_command`, `validate_git_repo`, `clone_repo`, `force_sync_repo`, `pull_repo`, `commit_and_push`, `get_status`, etc.
- **project_service**: `load_projects`, `save_project`, `get_projects`

## Roadmap (sugestões)

- Seleção granular de arquivos para commit (sem só `git add .`)
- Configuração de remoto/branch e checagem de URL ao sincronizar
- Testes automatizados (pytest) e empacotamento (PyInstaller / wheel)
- Internacionalização (i18n) ou tema claro
- Atalhos de teclado e histórico de comandos no log

## Autor

**Franklin** — [@nilknarfsam](https://github.com/nilknarfsam)

## Licença

Defina a licença desejada (por exemplo MIT) ao publicar o repositório.
