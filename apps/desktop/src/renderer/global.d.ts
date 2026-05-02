export {};

export type RunCommandResult = {
  code: number;
  stdout: string;
  stderr: string;
  error?: string;
};

declare global {
  interface Window {
    api: {
      runCommand(command: string, args: string[]): Promise<RunCommandResult>;
    };
  }
}
