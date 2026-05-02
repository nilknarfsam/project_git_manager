export function Header() {
  return (
    <header className="card">
      <div className="card-inner header-inner">
        <div className="header-brand">
          <span className="header-logo" aria-hidden="true" />
          <div>
            <h1 className="header-title">Project Git Manager</h1>
            <p className="header-subtitle">
              Desktop · integração com a CLI <code>projectgit</code>
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
