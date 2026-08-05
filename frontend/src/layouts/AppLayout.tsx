import { NavLink, Outlet } from "react-router-dom";


const navigationItems = [
  { label: "Overview", to: "/app/dashboard" },
  { label: "Projects", to: "/app/projects" },
  { label: "Agents", to: "/app/agents" },
  { label: "Deployments", to: "/app/deployments" },
  { label: "Approvals", to: "/app/approvals" },
  { label: "Usage", to: "/app/usage" },
  { label: "Observability", to: "/app/observability" },
  { label: "Governance", to: "/app/governance" },
  { label: "Marketplace", to: "/app/marketplace" },
];


export function AppLayout() {
  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div className="brand">
          <div className="brand-mark">Z</div>

          <div>
            <div className="brand-name">Zevinq</div>
            <div className="brand-subtitle">AI Control Plane</div>
          </div>
        </div>

        <nav className="sidebar-navigation">
          {navigationItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                isActive
                  ? "sidebar-link sidebar-link-active"
                  : "sidebar-link"
              }
            >
              <span className="sidebar-link-indicator" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="environment-badge">
            <span className="environment-dot" />
            Platform Online
          </div>

          <div className="sidebar-version">
            Zevinq Platform v0.1.0
          </div>
        </div>
      </aside>

      <div className="app-main">
        <header className="app-topbar">
          <div>
            <div className="topbar-context">Workspace</div>
            <div className="topbar-workspace">Zevinq Labs</div>
          </div>

          <div className="topbar-actions">
            <button
              type="button"
              className="topbar-button"
            >
              Docs
            </button>

            <div className="user-avatar">
              ZL
            </div>
          </div>
        </header>

        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
