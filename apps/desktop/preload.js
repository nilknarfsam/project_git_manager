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
});
