import { useCallback, useEffect, useState } from "react";

import { ActionButtons } from "./components/ActionButtons";
import { CloneModal } from "./components/CloneModal";
import { Header } from "./components/Header";
import { LogsPanel, type LogEntry, type LogLevel } from "./components/LogsPanel";
import { ProductivityActions } from "./components/ProductivityActions";
import { ProjectSelector } from "./components/ProjectSelector";
import { RepositoryInfo } from "./components/RepositoryInfo";
import type { SavedProject } from "./types/savedProject";
import { pathBasename } from "./utils/cloneValidation";
import {
  parseOverviewStdout,
  type RepositoryOverviewParsed,
} from "./utils/parseOverview";

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
  const [saveName, setSaveName] = useState("");
  const [projects, setProjects] = useState<SavedProject[]>([]);
  const [overview, setOverview] = useState<RepositoryOverviewParsed | null>(null);
  const [overviewLoading, setOverviewLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [entries, setEntries] = useState<LogEntry[]>([]);
  const [cloneModalOpen, setCloneModalOpen] = useState(false);
  const [cloneRunning, setCloneRunning] = useState(false);

  const appendLog = useCallback((level: LogLevel, text: string) => {
    setEntries((prev) => [...prev, { id: nextId(), level, text }]);
  }, []);

  const clearLogs = useCallback(() => {
    setEntries([]);
  }, []);

  const loadProjects = useCallback(async () => {
    const r = await window.api.getProjects();
    if (r.ok && r.projects) {
      setProjects(r.projects);
    } else {
      appendLog("error", r.error ?? "Não foi possível carregar os projetos salvos.");
    }
  }, [appendLog]);

  useEffect(() => {
    void loadProjects();
  }, [loadProjects]);

  const applyOverviewFromStdout = useCallback((stdout: string) => {
    if (!stdout.trim()) {
      setOverview(null);
      return;
    }
    setOverview(parseOverviewStdout(stdout));
  }, []);

  const refreshDashboard = useCallback(
    async (options?: { withLogs?: boolean }) => {
      const trimmed = path.trim();
      if (!trimmed) {
        setOverview(null);
        if (options?.withLogs) {
          appendLog("warning", "Informe o caminho do projeto.");
        }
        return;
      }

      setOverviewLoading(true);
      try {
        if (options?.withLogs) {
          appendLog("info", `▸ projectgit overview "${trimmed}"`);
        }
        const result = await window.api.runCommand("projectgit", [
          "overview",
          trimmed,
        ]);
        if (result.error) {
          appendLog("error", `Erro ao executar: ${result.error}`);
        }
        if (options?.withLogs) {
          appendLog("info", `Código de saída: ${result.code}`);
          if (result.stdout.trim()) {
            const level = classifyFromOutput(
              result.code,
              result.stdout,
              result.stderr,
            );
            appendLog(level, result.stdout.trimEnd());
          }
          if (result.stderr.trim()) {
            appendLog("warning", result.stderr.trimEnd());
          }
        }
        if (result.stdout.trim()) {
          applyOverviewFromStdout(result.stdout);
          appendLog(
            "success",
            options?.withLogs ? "Resumo obtido." : "Painel atualizado.",
          );
        } else {
          setOverview(null);
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        appendLog("error", msg);
        setOverview(null);
      } finally {
        setOverviewLoading(false);
      }
    },
    [appendLog, applyOverviewFromStdout, path],
  );

  const runGitSubcommand = useCallback(
    async (sub: "status" | "sync" | "overview") => {
      const trimmed = path.trim();
      if (!trimmed) {
        appendLog("warning", "Informe o caminho do projeto.");
        return;
      }

      setBusy(true);
      appendLog("info", `▸ projectgit ${sub} "${trimmed}"`);

      try {
        const result = await window.api.runCommand("projectgit", [sub, trimmed]);

        if (result.error) {
          appendLog("error", `Erro ao executar: ${result.error}`);
        }

        appendLog("info", `Código de saída: ${result.code}`);

        if (result.stdout.trim()) {
          const level = classifyFromOutput(
            result.code,
            result.stdout,
            result.stderr,
          );
          appendLog(level, result.stdout.trimEnd());
          if (sub === "overview") {
            applyOverviewFromStdout(result.stdout);
          }
        }
        if (result.stderr.trim()) {
          appendLog("warning", result.stderr.trimEnd());
        }

        if (sub === "sync" && result.code === 0) {
          await refreshDashboard();
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        appendLog("error", msg);
      } finally {
        setBusy(false);
      }
    },
    [appendLog, applyOverviewFromStdout, path, refreshDashboard],
  );

  const handleSelectFolder = useCallback(async () => {
    try {
      const r = await window.api.selectFolder();
      if (r.ok && r.path) {
        setPath(r.path);
        return;
      }
      if ("canceled" in r && r.canceled) return;
      appendLog("error", "error" in r && r.error ? r.error : "Falha ao selecionar pasta.");
    } catch (e) {
      appendLog("error", e instanceof Error ? e.message : String(e));
    }
  }, [appendLog]);

  const handleOpenVscode = useCallback(async () => {
    const trimmed = path.trim();
    if (!trimmed) {
      appendLog("warning", "Informe o caminho do projeto.");
      return;
    }
    try {
      const r = await window.api.openVscode(trimmed);
      if (r.ok) {
        appendLog("success", "VS Code iniciado.");
      } else {
        appendLog("error", r.error);
      }
    } catch (e) {
      appendLog("error", e instanceof Error ? e.message : String(e));
    }
  }, [appendLog, path]);

  const handleOpenCursor = useCallback(async () => {
    const trimmed = path.trim();
    if (!trimmed) {
      appendLog("warning", "Informe o caminho do projeto.");
      return;
    }
    try {
      const r = await window.api.openCursor(trimmed);
      if (r.ok) {
        appendLog("success", "Cursor iniciado.");
      } else {
        appendLog("error", r.error);
      }
    } catch (e) {
      appendLog("error", e instanceof Error ? e.message : String(e));
    }
  }, [appendLog, path]);

  const handleAfterClone = useCallback(
    async (destinationPath: string) => {
      const trimmed = destinationPath.trim();
      setPath(trimmed);
      const name = pathBasename(trimmed);
      const r = await window.api.saveProject({ name, path: trimmed });
      if (r.ok) {
        appendLog("success", `Favorito salvo automaticamente: ${name}`);
        await loadProjects();
      } else {
        appendLog("error", r.error ?? "Clone OK, mas falha ao salvar favorito.");
        await loadProjects();
      }
    },
    [appendLog, loadProjects],
  );

  const appendLogTyped = useCallback(
    (level: LogLevel, text: string) => {
      appendLog(level, text);
    },
    [appendLog],
  );

  const onSaveFavorite = useCallback(async () => {
    const trimmedPath = path.trim();
    const name = saveName.trim();
    if (!trimmedPath) {
      appendLog("warning", "Informe o caminho do projeto antes de salvar.");
      return;
    }
    if (!name) {
      appendLog("warning", "Informe um nome para o favorito.");
      return;
    }

    setBusy(true);
    try {
      const r = await window.api.saveProject({ name, path: trimmedPath });
      if (r.ok) {
        appendLog("success", `Projeto salvo: ${name}`);
        setSaveName("");
        await loadProjects();
      } else {
        appendLog("error", r.error ?? "Falha ao salvar.");
      }
    } catch (e) {
      appendLog("error", e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }, [appendLog, loadProjects, path, saveName]);

  const uiBusy = busy || overviewLoading || cloneRunning;

  return (
    <div className={`app-shell${uiBusy ? " app-shell--busy" : ""}`}>
      <Header />
      <ProjectSelector
        path={path}
        onPathChange={setPath}
        projects={projects}
        saveName={saveName}
        onSaveNameChange={setSaveName}
        onSaveFavorite={() => void onSaveFavorite()}
        onReloadProjects={() => void loadProjects()}
        onSelectFolder={() => void handleSelectFolder()}
        disabled={uiBusy}
      />
      <RepositoryInfo overview={overview} loading={overviewLoading} />
      <ProductivityActions
        busy={uiBusy}
        path={path}
        onOpenVscode={() => void handleOpenVscode()}
        onOpenCursor={() => void handleOpenCursor()}
        onOpenCloneModal={() => setCloneModalOpen(true)}
      />
      <ActionButtons
        busy={uiBusy}
        onStatus={() => void runGitSubcommand("status")}
        onSync={() => void runGitSubcommand("sync")}
        onResumo={() => void runGitSubcommand("overview")}
        onAtualizar={() => void refreshDashboard({ withLogs: false })}
      />
      <LogsPanel entries={entries} onClear={clearLogs} />
      <CloneModal
        open={cloneModalOpen}
        onClose={() => setCloneModalOpen(false)}
        disabled={busy || overviewLoading}
        onAfterClone={handleAfterClone}
        onLog={appendLogTyped}
        onCloneBusy={setCloneRunning}
      />
    </div>
  );
}
