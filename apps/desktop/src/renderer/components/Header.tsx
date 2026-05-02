export function Header() {
  return (
    <header className="card">
      <div className="card-inner header-inner">
        <div className="header-brand">
          <span className="header-logo" aria-hidden="true" />
          <div>
            <h1 className="header-title">Gerenciador de Projetos Git</h1>
            <p className="header-subtitle">
              Área de trabalho · integração com a CLI <code>projectgit</code> (sem
              duplicar lógica Git no app)
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
