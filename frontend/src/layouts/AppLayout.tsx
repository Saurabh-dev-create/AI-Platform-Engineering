import {
  NavLink,
  Outlet,
  useNavigate,
} from "react-router-dom";

import { clearAccessToken } from "../features/auth/auth-session";
import { useWorkspace } from "../features/workspaces/use-workspace";

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
  const navigate = useNavigate();

  const {
    currentWorkspace,
    isLoading: isWorkspaceLoading,
    isError: isWorkspaceError,
  } = useWorkspace();

  function handleLogout() {
    clearAccessToken();

    navigate(
      "/login",
      {
        replace: true,
      },
    );
  }

  let workspaceLabel = "Create workspace";

  if (isWorkspaceLoading) {
    workspaceLabel = "Loading workspace...";
  } else if (isWorkspaceError) {
    workspaceLabel = "Workspace unavailable";
  } else if (currentWorkspace) {
    workspaceLabel = currentWorkspace.name;
  }

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
            <div className="topbar-workspace">
              {workspaceLabel}
            </div>
          </div>

          <div className="topbar-actions">
            <button
              type="button"
              className="topbar-button"
            >
              Docs
            </button>

            <button
              type="button"
              className="topbar-button"
              onClick={handleLogout}
            >
              Logout
            </button>

            <button
              type="button"
              className="user-avatar user-avatar-button"
              onClick={() =>
                navigate("/app/profile/account")
              }
              aria-label="Open profile settings"
              title="Profile"
            >
              ZL
            </button>
          </div>
        </header>

        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
