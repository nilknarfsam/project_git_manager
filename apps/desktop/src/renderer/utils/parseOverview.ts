/** Estado derivado da saída textual de `projectgit overview` (pt-BR). */
export type RepositoryOverviewParsed = {
  projectName: string;
  branch: string;
  statusLine: string;
  lastCommit: string;
  /** true = Git válido; false = pasta sem Git ou inválida; null = não foi possível interpretar */
  isGitRepo: boolean | null;
};

function pickLine(lines: string[], prefix: string): string {
  const p = lines.find((l) => l.startsWith(prefix));
  if (!p) return "";
  return p.slice(prefix.length).trim();
}

/**
 * Interpreta stdout do comando `projectgit overview`.
 */
export function parseOverviewStdout(stdout: string): RepositoryOverviewParsed {
  const lines = stdout.split(/\r?\n/).map((l) => l.trimEnd());
  const projectName = pickLine(lines, "Projeto:");
  const branch = pickLine(lines, "Branch:");
  const statusLine = pickLine(lines, "Status:");
  const lastCommit = pickLine(lines, "Último commit:");

  let isGitRepo: boolean | null = null;
  if (/Não é repositório|não é um repositório/i.test(statusLine)) {
    isGitRepo = false;
  } else if (branch && branch !== "—" && branch !== "-") {
    isGitRepo = true;
  } else if (statusLine && !/Nenhuma pasta/i.test(statusLine)) {
    isGitRepo = /Limpo|Alterações|HEAD|⚠|✔/u.test(statusLine) ? true : null;
  }

  return {
    projectName: projectName || "—",
    branch: branch || "—",
    statusLine: statusLine || "—",
    lastCommit: lastCommit || "—",
    isGitRepo,
  };
}
