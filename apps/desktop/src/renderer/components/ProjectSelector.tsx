import type { SavedProject } from "../types/savedProject";

type ProjectSelectorProps = {
  path: string;
  onPathChange: (value: string) => void;
  projects: SavedProject[];
  saveName: string;
  onSaveNameChange: (value: string) => void;
  onSaveFavorite: () => void;
  onReloadProjects: () => void;
  disabled: boolean;
};

export function ProjectSelector({
  path,
  onPathChange,
  projects,
  saveName,
  onSaveNameChange,
  onSaveFavorite,
  onReloadProjects,
  disabled,
}: ProjectSelectorProps) {
  const selectValue =
    projects.find((p) => p.path === path)?.name ?? "__manual__";

  return (
    <section className="card" aria-label="Projeto e favoritos">
      <div className="card-inner">
        <label className="field-label" htmlFor="repo-path">
          Caminho do projeto
        </label>
        <input
          id="repo-path"
          className="field-input"
          type="text"
          placeholder="Ex.: C:\src\projects\auratime"
          value={path}
          onChange={(e) => onPathChange(e.target.value)}
          disabled={disabled}
          autoComplete="off"
          spellCheck={false}
        />

        <div className="field-row field-row--split">
          <div className="field-grow">
            <label className="field-label" htmlFor="saved-projects">
              Projetos salvos
            </label>
            <select
              id="saved-projects"
              className="field-select"
              value={selectValue}
              disabled={disabled}
              onChange={(e) => {
                const v = e.target.value;
                if (v === "__manual__") return;
                const hit = projects.find((p) => p.name === v);
                if (hit) onPathChange(hit.path);
              }}
            >
              <option value="__manual__">— escolher na lista —</option>
              {projects.map((p) => (
                <option key={p.name} value={p.name}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field-actions">
            <button
              type="button"
              className="btn btn-ghost"
              disabled={disabled}
              onClick={onReloadProjects}
            >
              Recarregar lista
            </button>
          </div>
        </div>

        <div className="save-favorite">
          <label className="field-label" htmlFor="save-name">
            Salvar nos favoritos
          </label>
          <div className="field-row field-row--save">
            <input
              id="save-name"
              className="field-input field-input--grow"
              type="text"
              placeholder="Nome do projeto"
              value={saveName}
              onChange={(e) => onSaveNameChange(e.target.value)}
              disabled={disabled}
              autoComplete="off"
            />
            <button
              type="button"
              className="btn btn-secondary"
              disabled={disabled}
              onClick={onSaveFavorite}
            >
              Salvar
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
