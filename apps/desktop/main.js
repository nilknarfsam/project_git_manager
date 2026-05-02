"use strict";

const { app, BrowserWindow, ipcMain } = require("electron");
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

let mainWindow = null;

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
