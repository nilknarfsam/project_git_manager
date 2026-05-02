export type RunCommandResult = {
  code: number;
  stdout: string;
  stderr: string;
  error?: string;
};

export type GetProjectsResult = {
  ok: boolean;
  projects?: { name: string; path: string }[];
  error?: string;
};

export type SaveProjectResult = {
  ok: boolean;
  error?: string;
};

export type SelectFolderResult =
  | { ok: true; path: string }
  | { ok: false; canceled?: boolean; error?: string };

export type OpenEditorResult = { ok: true } | { ok: false; error: string };

declare global {
  interface Window {
    api: {
      runCommand(command: string, args: string[]): Promise<RunCommandResult>;
      getProjects(): Promise<GetProjectsResult>;
      saveProject(entry: {
        name: string;
        path: string;
      }): Promise<SaveProjectResult>;
      selectFolder(): Promise<SelectFolderResult>;
      openVscode(targetPath: string): Promise<OpenEditorResult>;
      openCursor(targetPath: string): Promise<OpenEditorResult>;
    };
  }
}

export {};
