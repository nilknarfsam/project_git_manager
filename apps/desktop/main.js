"use strict";

const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

/** Comando permitido no IPC (evita spawn arbitrário). */
const ALLOWED_COMMANDS = new Set(["projectgit"]);

const isDev =
  process.env.ELECTRON_DEV === "1" ||
  process.env.ELECTRON_DEV === "true";

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
