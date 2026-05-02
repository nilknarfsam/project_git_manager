type ProductivityActionsProps = {
  busy: boolean;
  path: string;
  onOpenVscode: () => void;
  onOpenCursor: () => void;
  onOpenCloneModal: () => void;
};

export function ProductivityActions({
  busy,
  path,
  onOpenVscode,
  onOpenCursor,
  onOpenCloneModal,
}: ProductivityActionsProps) {
  const hasPath = path.trim().length > 0;

  return (
    <section className="card actions-card" aria-label="Produtividade">
      <div className="card-inner">
        <h2 className="panel-title">Produtividade</h2>
        <p className="actions-hint">
          Abre a pasta atual no editor ou clone um repositório remoto via{" "}
          <code>projectgit</code>.
        </p>
        <div className="button-row">
          <button
            type="button"
            className="btn btn-accent"
            disabled={busy || !hasPath}
            onClick={onOpenVscode}
          >
            Abrir no VS Code
          </button>
          <button
            type="button"
            className="btn btn-accent"
            disabled={busy || !hasPath}
            onClick={onOpenCursor}
          >
            Abrir no Cursor
          </button>
          <button type="button" className="btn btn-secondary" disabled={busy} onClick={onOpenCloneModal}>
            Clonar repositório
          </button>
        </div>
      </div>
    </section>
  );
}
