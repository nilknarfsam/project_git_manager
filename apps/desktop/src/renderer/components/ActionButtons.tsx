type ActionButtonsProps = {
  busy: boolean;
  onStatus: () => void;
  onSync: () => void;
  onResumo: () => void;
  onAtualizar: () => void;
};

export function ActionButtons({
  busy,
  onStatus,
  onSync,
  onResumo,
  onAtualizar,
}: ActionButtonsProps) {
  return (
    <section className="card actions-card" aria-label="Ações Git">
      <div className="card-inner">
        <h2 className="panel-title">Ações</h2>
        <p className="actions-hint">
          Sincronizar alinha com o remoto e pode descartar alterações locais.
        </p>
        <div className="button-row">
          <button
            type="button"
            className="btn btn-primary"
            disabled={busy}
            onClick={onStatus}
          >
            Status
          </button>
          <button
            type="button"
            className="btn btn-warn"
            disabled={busy}
            onClick={onSync}
          >
            Sincronizar
          </button>
          <button
            type="button"
            className="btn btn-accent"
            disabled={busy}
            onClick={onResumo}
          >
            Resumo
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            disabled={busy}
            onClick={onAtualizar}
          >
            Atualizar
          </button>
        </div>
      </div>
    </section>
  );
}
