import { useCallback, useEffect, useState } from "react";

import { isSafeCloneDestinationPath, isValidGitCloneUrl } from "../utils/cloneValidation";

type CloneModalProps = {
  open: boolean;
  onClose: () => void;
  disabled: boolean;
  onAfterClone: (destinationPath: string) => Promise<void>;
  onLog: (level: "info" | "success" | "warning" | "error", text: string) => void;
  onCloneBusy?: (busy: boolean) => void;
};

type Phase = "idle" | "cloning" | "done" | "error";

export function CloneModal({
  open,
  onClose,
  disabled,
  onAfterClone,
  onLog,
  onCloneBusy,
}: CloneModalProps) {
  const [url, setUrl] = useState("");
  const [dest, setDest] = useState("");
  const [phase, setPhase] = useState<Phase>("idle");
  const [detail, setDetail] = useState("");

  useEffect(() => {
    if (!open) {
      setPhase("idle");
      setDetail("");
    }
  }, [open]);

  const pickDestFolder = useCallback(async () => {
    const r = await window.api.selectFolder();
    if (r.ok) {
      setDest(r.path);
      return;
    }
    if ("canceled" in r && r.canceled) return;
    onLog("error", "error" in r && r.error ? r.error : "Não foi possível escolher a pasta.");
  }, [onLog]);

  const runClone = useCallback(async () => {
    const u = url.trim();
    const d = dest.trim();

    if (!isValidGitCloneUrl(u)) {
      onLog("warning", "URL do repositório inválida.");
      setPhase("error");
      setDetail("Informe uma URL https, git@, ssh:// ou git:// válida.");
      return;
    }
    if (!isSafeCloneDestinationPath(d)) {
      onLog("warning", "Caminho de destino inválido.");
      setPhase("error");
      setDetail("Informe um caminho completo válido para a pasta do clone.");
      return;
    }

    setPhase("cloning");
    setDetail("Clonando...");
    onCloneBusy?.(true);
    onLog("info", `▸ projectgit clone "${u}" "${d}"`);

    try {
      const result = await window.api.runCommand("projectgit", ["clone", u, d]);

      if (result.error) {
        onLog("error", `Erro ao executar: ${result.error}`);
        setPhase("error");
        setDetail("Erro ao clonar");
        return;
      }

      if (result.stdout.trim()) {
        onLog("info", result.stdout.trimEnd());
      }
      if (result.stderr.trim()) {
        onLog("warning", result.stderr.trimEnd());
      }

      if (result.code !== 0) {
        setPhase("error");
        setDetail("Erro ao clonar");
        onLog("error", "Clone falhou (código de saída diferente de zero).");
        return;
      }

      setPhase("done");
      setDetail("Clone concluído");
      onLog("success", "Clone concluído");

      await onAfterClone(d);
      onClose();
      setUrl("");
      setDest("");
      setPhase("idle");
      setDetail("");
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      onLog("error", msg);
      setPhase("error");
      setDetail("Erro ao clonar");
    } finally {
      onCloneBusy?.(false);
    }
  }, [url, dest, onAfterClone, onClose, onLog, onCloneBusy]);

  if (!open) return null;

  const busy = phase === "cloning" || disabled;

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="modal-dialog card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="clone-modal-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="card-inner modal-dialog-inner">
          <h2 id="clone-modal-title" className="panel-title">
            Clonar repositório
          </h2>
          <p className="modal-hint">
            O destino deve ser o caminho completo da pasta do clone (incluindo o nome da pasta),
            como no app legado.
          </p>

          <label className="field-label" htmlFor="clone-url">
            URL do repositório
          </label>
          <input
            id="clone-url"
            className="field-input"
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={busy}
            placeholder="https://github.com/org/repo.git"
            autoComplete="off"
            spellCheck={false}
          />

          <label className="field-label field-label--gap" htmlFor="clone-dest">
            Caminho destino
          </label>
          <div className="path-input-row">
            <input
              id="clone-dest"
              className="field-input path-input-row__input"
              type="text"
              value={dest}
              onChange={(e) => setDest(e.target.value)}
              disabled={busy}
              placeholder="Ex.: C:\src\projects\meu-repo"
              autoComplete="off"
              spellCheck={false}
            />
            <button
              type="button"
              className="btn btn-ghost btn-sm path-input-row__btn"
              disabled={busy}
              onClick={() => void pickDestFolder()}
            >
              Selecionar pasta
            </button>
          </div>

          {detail ? (
            <p
              className={`clone-status clone-status--${phase === "error" ? "err" : phase === "done" ? "ok" : "muted"}`}
            >
              {detail}
            </p>
          ) : null}

          <div className="modal-actions">
            <button type="button" className="btn btn-ghost" disabled={busy} onClick={onClose}>
              Cancelar
            </button>
            <button type="button" className="btn btn-primary" disabled={busy} onClick={() => void runClone()}>
              Clonar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
