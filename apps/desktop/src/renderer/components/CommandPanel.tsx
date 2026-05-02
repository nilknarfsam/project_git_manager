type SubCommand = "status" | "sync" | "overview";

type CommandPanelProps = {
  path: string;
  onPathChange: (value: string) => void;
  busy: boolean;
  onRun: (sub: SubCommand) => void;
};

export function CommandPanel({
  path,
  onPathChange,
  busy,
  onRun,
}: CommandPanelProps) {
  return (
    <section className="card command-card" aria-label="Comandos">
      <div className="card-inner">
        <label className="field-label" htmlFor="repo-path">
          Caminho do repositório
        </label>
        <input
          id="repo-path"
          className="field-input"
          type="text"
          placeholder="Ex.: C:\src\projects\auratime"
          value={path}
          onChange={(e) => onPathChange(e.target.value)}
          disabled={busy}
          autoComplete="off"
          spellCheck={false}
        />
        <div className="button-row">
          <button
            type="button"
            className="btn btn-primary"
            disabled={busy}
            onClick={() => onRun("status")}
          >
            Status
          </button>
          <button
            type="button"
            className="btn btn-warn"
            disabled={busy}
            onClick={() => onRun("sync")}
          >
            Sync
          </button>
          <button
            type="button"
            className="btn btn-accent"
            disabled={busy}
            onClick={() => onRun("overview")}
          >
            Overview
          </button>
        </div>
      </div>
    </section>
  );
}
