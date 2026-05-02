"use strict";

const { app, BrowserWindow, dialog, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs/promises");
const { spawn } = require("child_process");

/** Comando permitido no IPC (evita spawn arbitrário). */
const ALLOWED_COMMANDS = new Set(["projectgit"]);

const isDev =
  process.env.ELECTRON_DEV === "1" ||
  process.env.ELECTRON_DEV === "true";

/**
 * Caminho de `projects.json` (mesmo arquivo do app CustomTkinter em
 * `legacy_python/customtkinter_app/data/`). Sobrescreva com PROJECTGIT_PROJECTS_JSON.
 */
function getProjectsFilePath() {
  if (process.env.PROJECTGIT_PROJECTS_JSON?.trim()) {
    return process.env.PROJECTGIT_PROJECTS_JSON.trim();
  }
  const repoRoot = path.join(__dirname, "..", "..");
  return path.join(
    repoRoot,
    "legacy_python",
    "customtkinter_app",
    "data",
    "projects.json",
  );
}

/**
 * Executável `projectgit`. Em Windows, use PATH (Scripts do venv) ou defina PROJECTGIT_BIN
 * com caminho absoluto para projectgit.exe.
 */
function resolveProjectGitExecutable() {
  if (process.env.PROJECTGIT_BIN && process.env.PROJECTGIT_BIN.trim()) {
    return process.env.PROJECTGIT_BIN.trim();
  }
  return "projectgit";
}

function validateArgs(args) {
  if (!Array.isArray(args)) {
    return "args deve ser um array de strings.";
  }
  for (const a of args) {
    if (typeof a !== "string") {
      return "cada argumento deve ser string.";
    }
  }
  return null;
}

/** Rejeita caracteres de controle e caminhos absurdamente longos (spawn seguro). */
function assertPlainPathString(s) {
  if (typeof s !== "string") {
    return { ok: false, error: "Caminho inválido." };
  }
  const t = s.trim();
  if (!t) {
    return { ok: false, error: "Caminho vazio." };
  }
  if (t.length > 4096) {
    return { ok: false, error: "Caminho muito longo." };
  }
  if (/[\0\r\n\x0b]/.test(t)) {
    return { ok: false, error: "Caracteres inválidos no caminho." };
  }
  return { ok: true, trimmed: t };
}

/**
 * Resolve e verifica se existe como diretório (antes de abrir no editor).
 * @param {unknown} rawPath
 * @returns {Promise<{ ok: true; path: string } | { ok: false; error: string }>}
 */
async function validateDirectoryForOpen(rawPath) {
  const base = assertPlainPathString(rawPath);
  if (!base.ok) {
    return base;
  }
  let resolved;
  try {
    resolved = path.resolve(base.trimmed);
  } catch {
    return { ok: false, error: "Não foi possível resolver o caminho." };
  }
  try {
    const st = await fs.stat(resolved);
    if (!st.isDirectory()) {
      return { ok: false, error: "O caminho não é uma pasta." };
    }
  } catch (e) {
    const code = /** @type {NodeJS.ErrnoException} */ (e).code;
    if (code === "ENOENT") {
      return { ok: false, error: "Pasta não encontrada." };
    }
    return {
      ok: false,
      error: e instanceof Error ? e.message : String(e),
    };
  }
  return { ok: true, path: resolved };
}

/**
 * @param {string} bin ex.: "code" ou "code.cmd"
 * @param {string} folderPath caminho já validado
 * @returns {Promise<{ ok: true } | { ok: false; error: string }>}
 */
function spawnEditorDetached(bin, folderPath) {
  return new Promise((resolve) => {
    let settled = false;
    const child = spawn(bin, [folderPath], {
      shell: false,
      windowsHide: true,
      detached: true,
      stdio: "ignore",
    });
    child.once("error", (err) => {
      if (settled) return;
      settled = true;
      resolve({
        ok: false,
        error: `Não foi possível iniciar o editor (${bin}). Verifique se está no PATH. ${err.message}`,
      });
    });
    child.once("spawn", () => {
      if (settled) return;
      settled = true;
      child.unref();
      resolve({ ok: true });
    });
  });
}

/** Ordem: preferir .cmd no Windows (shell off), depois o binário base. */
function editorBinaryCandidates(base) {
  if (process.platform === "win32") {
    return [`${base}.cmd`, base];
  }
  return [base];
}

/**
 * @param {string[]} bins
 * @param {string} folderPath
 */
async function spawnFirstAvailableEditor(bins, folderPath) {
  let lastError = "Não foi possível iniciar o editor.";
  for (const bin of bins) {
    const r = await spawnEditorDetached(bin, folderPath);
    if (r.ok) {
      return r;
    }
    lastError = r.error;
  }
  return { ok: false, error: lastError };
}

let mainWindow = null;

/**
 * @param {string} command
 * @param {string[]} args
 * @returns {Promise<{ code: number; stdout: string; stderr: string; error?: string }>}
 */
function runSpawn(command, args) {
  return new Promise((resolve) => {
    const child = spawn(command, args, {
      shell: false,
      windowsHide: true,
      env: process.env,
    });

    let stdout = "";
    let stderr = "";

    child.stdout?.setEncoding("utf8");
    child.stderr?.setEncoding("utf8");
    child.stdout?.on("data", (chunk) => {
      stdout += chunk;
    });
    child.stderr?.on("data", (chunk) => {
      stderr += chunk;
    });

    child.on("error", (err) => {
      resolve({
        code: -1,
        stdout,
        stderr,
        error: err.message,
      });
    });

    child.on("close", (code, signal) => {
      const exitCode = typeof code === "number" ? code : signal ? -1 : 0;
      resolve({ code: exitCode, stdout, stderr });
    });
  });
}

ipcMain.handle("run-command", async (_event, command, args) => {
  if (typeof command !== "string" || !ALLOWED_COMMANDS.has(command)) {
    return {
      code: -1,
      stdout: "",
      stderr: "",
      error: `Comando não permitido: ${String(command)}`,
    };
  }

  const argErr = validateArgs(args);
  if (argErr) {
    return { code: -1, stdout: "", stderr: "", error: argErr };
  }

  const executable = resolveProjectGitExecutable();
  return runSpawn(executable, args);
});

ipcMain.handle("get-projects", async () => {
  const filePath = getProjectsFilePath();
  try {
    const raw = await fs.readFile(filePath, "utf8");
    const data = JSON.parse(raw);
    if (!Array.isArray(data)) {
      return { ok: true, projects: [] };
    }
    const projects = [];
    for (const item of data) {
      if (
        item &&
        typeof item === "object" &&
        typeof item.name === "string" &&
        typeof item.path === "string"
      ) {
        projects.push({ name: item.name, path: item.path });
      }
    }
    return { ok: true, projects };
  } catch (e) {
    if (/** @type {NodeJS.ErrnoException} */ (e).code === "ENOENT") {
      return { ok: true, projects: [] };
    }
    return {
      ok: false,
      projects: [],
      error: e instanceof Error ? e.message : String(e),
    };
  }
});

ipcMain.handle("select-folder", async () => {
  const win = BrowserWindow.getFocusedWindow() ?? mainWindow;
  const result = await dialog.showOpenDialog(win ?? undefined, {
    properties: ["openDirectory", "createDirectory"],
  });
  if (result.canceled || !result.filePaths?.length) {
    return { ok: false, canceled: true };
  }
  return { ok: true, path: result.filePaths[0] };
});

ipcMain.handle("open-vscode", async (_event, targetPath) => {
  const v = await validateDirectoryForOpen(targetPath);
  if (!v.ok) {
    return v;
  }
  return spawnFirstAvailableEditor(editorBinaryCandidates("code"), v.path);
});

ipcMain.handle("open-cursor", async (_event, targetPath) => {
  const v = await validateDirectoryForOpen(targetPath);
  if (!v.ok) {
    return v;
  }
  return spawnFirstAvailableEditor(editorBinaryCandidates("cursor"), v.path);
});

ipcMain.handle("save-project", async (_event, payload) => {
  const name =
    typeof payload?.name === "string" ? payload.name.trim() : "";
  const rawPath =
    typeof payload?.path === "string" ? payload.path.trim() : "";
  if (!name) {
    return { ok: false, error: "Informe um nome de projeto." };
  }
  if (!rawPath) {
    return { ok: false, error: "Informe um caminho válido." };
  }

  let pathNorm;
  try {
    pathNorm = path.resolve(rawPath);
  } catch (e) {
    return { ok: false, error: "Caminho inválido." };
  }

  const filePath = getProjectsFilePath();
  let list = [];
  try {
    const raw = await fs.readFile(filePath, "utf8");
    const data = JSON.parse(raw);
    if (Array.isArray(data)) {
      list = data.filter(
        (p) =>
          p &&
          typeof p === "object" &&
          typeof p.name === "string" &&
          typeof p.path === "string",
      );
    }
  } catch (e) {
    if (/** @type {NodeJS.ErrnoException} */ (e).code !== "ENOENT") {
      return {
        ok: false,
        error: e instanceof Error ? e.message : String(e),
      };
    }
  }

  const filtered = list.filter((p) => {
    try {
      return path.resolve(p.path) !== pathNorm;
    } catch {
      return true;
    }
  });
  const deduped = filtered.filter(
    (p) => p.name.toLowerCase() !== name.toLowerCase(),
  );
  deduped.push({ name, path: pathNorm });

  try {
    await fs.mkdir(path.dirname(filePath), { recursive: true });
    await fs.writeFile(
      filePath,
      JSON.stringify(deduped, null, 2),
      "utf8",
    );
    return { ok: true };
  } catch (e) {
    return {
      ok: false,
      error: e instanceof Error ? e.message : String(e),
    };
  }
});

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 960,
    height: 720,
    minWidth: 640,
    minHeight: 480,
    backgroundColor: "#0d1117",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  if (isDev) {
    mainWindow.loadURL("http://127.0.0.1:5173/");
    mainWindow.webContents.openDevTools({ mode: "detach" });
  } else {
    mainWindow.loadFile(path.join(__dirname, "dist", "index.html"));
  }
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
