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

declare global {
  interface Window {
    api: {
      runCommand(command: string, args: string[]): Promise<RunCommandResult>;
      getProjects(): Promise<GetProjectsResult>;
      saveProject(entry: {
        name: string;
        path: string;
      }): Promise<SaveProjectResult>;
    };
  }
}

export {};
