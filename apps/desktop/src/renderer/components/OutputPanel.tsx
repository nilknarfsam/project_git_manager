export type LogLevel = "info" | "success" | "warning" | "error";

export type LogEntry = {
  id: string;
  level: LogLevel;
  text: string;
};

type OutputPanelProps = {
  entries: LogEntry[];
  onClear: () => void;
};

export function OutputPanel({ entries, onClear }: OutputPanelProps) {
  return (
    <section className="card output-card" aria-label="Saída">
      <div className="card-inner output-header">
        <h2 className="panel-title">Logs</h2>
        <button type="button" className="btn btn-ghost btn-sm" onClick={onClear}>
          Limpar
        </button>
      </div>
      <div className="output-scroll" role="log" aria-live="polite">
        {entries.length === 0 ? (
          <p className="log-line log-line--info">Nenhuma saída ainda.</p>
        ) : (
          entries.map((e) => (
            <p key={e.id} className={`log-line log-line--${e.level}`}>
              {e.text}
            </p>
          ))
        )}
      </div>
    </section>
  );
}
