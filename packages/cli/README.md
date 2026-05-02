# CLI `projectgit`

Usa o pacote `project_git_core` (`packages/core`). Não duplica lógica Git.

## Instalação (modo dev)

Na raiz do monorepo:

```bash
pip install -e packages/core
pip install -e packages/cli
```

Instale **sempre o core antes** da CLI (a dependência declara `project-git-core`).

Isso registra o comando `projectgit` no ambiente ativo.

## Uso

```bash
projectgit overview C:\src\projects\auratime
projectgit status C:\src\projects\auratime
projectgit pull C:\src\projects\auratime
projectgit sync C:\src\projects\auratime
projectgit clone https://github.com/org/repo.git C:\src\repo
projectgit commit C:\src\projects\auratime -m "mensagem do commit"
```

## Execução sem `pip install` (fallback)

Se `project_git_core` não estiver instalado, o pacote `projectgit` ainda injeta `packages/core` e `packages/cli` no `sys.path` a partir do layout do monorepo.

Na pasta `packages/cli`:

```bash
python -m projectgit.main status "C:\src\projects\auratime"
python -m projectgit overview "C:\src\projects\auratime"
python -m projectgit
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
