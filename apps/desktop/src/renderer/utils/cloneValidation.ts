/** Caminho local seguro para enviar ao CLI (sem shell). */
export function isSafeCloneDestinationPath(p: string): boolean {
  const t = p.trim();
  if (!t || t.length > 4096) return false;
  if (/[\0\r\n\x0b]/.test(t)) return false;
  return true;
}

/** Valida URL de clone antes de chamar o backend. */
export function isValidGitCloneUrl(url: string): boolean {
  const u = url.trim();
  if (!u || u.length > 2048) return false;
  if (/[\0\r\n\x0b]/.test(u)) return false;

  if (/^https?:\/\//i.test(u)) {
    try {
      const parsed = new URL(u);
      return Boolean(parsed.hostname);
    } catch {
      return false;
    }
  }

  if (/^git@[^:\s]+:[^\s]+/i.test(u)) return true;

  if (/^ssh:\/\//i.test(u)) {
    try {
      return Boolean(new URL(u).hostname);
    } catch {
      return false;
    }
  }

  if (/^git:\/\//i.test(u)) return true;

  return false;
}

export function pathBasename(folderPath: string): string {
  const t = folderPath.trim().replace(/[/\\]+$/, "");
  const i = Math.max(t.lastIndexOf("/"), t.lastIndexOf("\\"));
  const name = i >= 0 ? t.slice(i + 1) : t;
  return name || "projeto";
}
