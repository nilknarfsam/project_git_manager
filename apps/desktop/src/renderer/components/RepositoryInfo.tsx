import type { RepositoryOverviewParsed } from "../utils/parseOverview";

type RepositoryInfoProps = {
  overview: RepositoryOverviewParsed | null;
  loading: boolean;
};

function statusTone(
  isGitRepo: boolean | null,
  statusLine: string,
): "ok" | "warn" | "err" | "muted" {
  if (isGitRepo === false) return "err";
  if (/⚠/u.test(statusLine) || /pendentes|HEAD|aviso/i.test(statusLine)) {
    return "warn";
  }
  if (/✔/u.test(statusLine) || /Limpo/i.test(statusLine)) return "ok";
  return "muted";
}

export function RepositoryInfo({ overview, loading }: RepositoryInfoProps) {
  if (loading) {
    return (
      <section className="card repo-card" aria-label="Resumo do repositório">
        <div className="card-inner">
          <h2 className="panel-title">Resumo do repositório</h2>
          <p className="loading-line" aria-busy="true">
            Carregando resumo…
          </p>
        </div>
      </section>
    );
  }

  const o = overview ?? {
    projectName: "—",
    branch: "—",
    statusLine: "—",
    lastCommit: "—",
    isGitRepo: null,
  };

  const tone = statusTone(o.isGitRepo, o.statusLine);

  return (
    <section className="card repo-card" aria-label="Resumo do repositório">
      <div className="card-inner">
        <h2 className="panel-title">Resumo do repositório</h2>
        <dl className="repo-grid">
          <div className="repo-row">
            <dt>Nome do projeto atual</dt>
            <dd>{o.projectName}</dd>
          </div>
          <div className="repo-row">
            <dt>Branch</dt>
            <dd>{o.branch}</dd>
          </div>
          <div className="repo-row">
            <dt>Status</dt>
            <dd>
              <span className={`status-pill status-pill--${tone}`}>
                {o.statusLine}
              </span>
            </dd>
          </div>
          <div className="repo-row">
            <dt>Último commit</dt>
            <dd className="repo-commit">{o.lastCommit}</dd>
          </div>
        </dl>
      </div>
    </section>
  );
}
