# CLI `projectgit`

Usa o pacote `project_git_core` (`packages/core`). Não duplica lógica Git.

## Execução sem `pip install`

Na pasta `packages/cli` do repositório:

```bash
python -m projectgit.main status "C:\src\projects\auratime"
python -m projectgit overview "C:\src\projects\auratime"
python -m projectgit
```

Atalho equivalente:

```bash
python -m projectgit overview "C:\src\projects\auratime"
```

## Comandos

| Comando | Descrição |
|---------|-----------|
| `status PATH` | `git status` |
| `sync PATH` | Sincronização forçada com `origin` (destructiva) |
| `clone URL DEST` | Clone ou sync se `DEST` já for repo Git |
| `pull PATH` | `git pull` |
| `commit PATH -m "msg"` | `add` + `commit` + `push` |
| `overview PATH` | Resumo: branch, limpo/sujo, último commit |

## Futuro

Ver comentários em `pyproject.toml` para `pip install -e .` e o entrypoint `projectgit`.
