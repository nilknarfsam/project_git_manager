"use strict";

const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  /**
   * Executa um comando permitido no processo principal (spawn, sem shell).
   * @param {string} command ex.: "projectgit"
   * @param {string[]} args ex.: ["overview", "C:\\src\\repo"]
   * @returns {Promise<{ code: number; stdout: string; stderr: string; error?: string }>}
   */
  runCommand(command, args) {
    return ipcRenderer.invoke("run-command", command, args);
  },
});
