import { useCallback, useMemo, useState } from "react";

import { CommandPanel } from "./components/CommandPanel";
import { Header } from "./components/Header";
import { type LogEntry, type LogLevel, OutputPanel } from "./components/OutputPanel";

let logId = 0;
function nextId(): string {
  logId += 1;
  return `log-${logId}`;
}

function classifyFromOutput(code: number, stdout: string, stderr: string): LogLevel {
  if (code !== 0) return "error";
  const combined = `${stdout}\n${stderr}`;
  if (/❌/u.test(combined) || /falhou|error|fatal/i.test(combined)) return "error";
  if (/⚠/u.test(combined) || /aviso|warning/i.test(combined)) return "warning";
  if (/✔/u.test(combined) || /success|concluíd/i.test(combined)) return "success";
  return "success";
}

export default function App() {
  const [path, setPath] = useState("");
  const [busy, setBusy] = useState(false);
  const [entries, setEntries] = useState<LogEntry[]>([]);

  const appendLog = useCallback((level: LogLevel, text: string) => {
    setEntries((prev) => [...prev, { id: nextId(), level, text }]);
  }, []);

  const clearLogs = useCallback(() => {
    setEntries([]);
  }, []);

  const runSub = useCallback(
    async (sub: "status" | "sync" | "overview") => {
      const trimmed = path.trim();
      if (!trimmed) {
        appendLog("warning", "Informe o caminho do repositório.");
        return;
      }

      setBusy(true);
      appendLog("info", `▸ projectgit ${sub} "${trimmed}"`);

      try {
        const result = await window.api.runCommand("projectgit", [sub, trimmed]);

        if (result.error) {
          appendLog("error", `Spawn / IPC: ${result.error}`);
        }

        appendLog("info", `Código de saída: ${result.code}`);

        if (result.stdout.trim()) {
          const level = classifyFromOutput(result.code, result.stdout, result.stderr);
          appendLog(level, result.stdout.trimEnd());
        }
        if (result.stderr.trim()) {
          appendLog("warning", result.stderr.trimEnd());
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        appendLog("error", `Erro: ${msg}`);
      } finally {
        setBusy(false);
      }
    },
    [appendLog, path],
  );

  const bodyClass = useMemo(() => `app-shell${busy ? " app-shell--busy" : ""}`, [busy]);

  return (
    <div className={bodyClass}>
      <Header />
      <CommandPanel
        path={path}
        onPathChange={setPath}
        busy={busy}
        onRun={runSub}
      />
      <OutputPanel entries={entries} onClear={clearLogs} />
    </div>
  );
}
