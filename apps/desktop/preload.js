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

  /**
   * Lista projetos favoritos (mesmo JSON do app Python).
   * @returns {Promise<{ ok: boolean; projects?: { name: string; path: string }[]; error?: string }>}
   */
  getProjects() {
    return ipcRenderer.invoke("get-projects");
  },

  /**
   * Salva ou atualiza um favorito.
   * @param {{ name: string; path: string }} entry
   * @returns {Promise<{ ok: boolean; error?: string }>}
   */
  saveProject(entry) {
    return ipcRenderer.invoke("save-project", entry);
  },

  /**
   * Abre diálogo nativo para escolher uma pasta.
   * @returns {Promise<{ ok: true; path: string } | { ok: false; canceled?: boolean; error?: string }>}
   */
  selectFolder() {
    return ipcRenderer.invoke("select-folder");
  },

  /**
   * Abre a pasta no VS Code (spawn sem shell).
   * @param {string} targetPath
   * @returns {Promise<{ ok: true } | { ok: false; error: string }>}
   */
  openVscode(targetPath) {
    return ipcRenderer.invoke("open-vscode", targetPath);
  },

  /**
   * Abre a pasta no Cursor (spawn sem shell).
   * @param {string} targetPath
   * @returns {Promise<{ ok: true } | { ok: false; error: string }>}
   */
  openCursor(targetPath) {
    return ipcRenderer.invoke("open-cursor", targetPath);
  },
});
