import { Link } from "react-router-dom";

const capabilities = [
  {
    title: "Agent Registry",
    description:
      "Register and organize AI agents across teams, projects, and environments.",
  },
  {
    title: "Version Management",
    description:
      "Manage agent configuration, prompts, models, tools, and runtime versions.",
  },
  {
    title: "Deployment Control",
    description:
      "Coordinate development, staging, and production deployment lifecycles.",
  },
  {
    title: "Governance",
    description:
      "Build approval, policy, access-control, and compliance workflows around AI operations.",
  },
  {
    title: "Usage & Cost",
    description:
      "Bring token consumption, provider usage, budgets, and cost visibility into one control plane.",
  },
  {
    title: "Observability",
    description:
      "Create operational visibility for AI agents, deployments, latency, failures, and platform health.",
  },
];

export function LandingPage() {
  return (
    <main className="landing-page">
      <header className="landing-header">
        <Link
          to="/"
          className="landing-brand"
        >
          <span className="landing-brand-mark">
            Z
          </span>

          <span>
            <strong>Zevinq</strong>
            <small>Labs</small>
          </span>
        </Link>

        <nav className="landing-navigation">
          <a href="#platform">Platform</a>
          <a href="#capabilities">Capabilities</a>
          <a href="#architecture">Architecture</a>

          <Link
            to="/login"
            className="landing-sign-in"
          >
            Sign in
          </Link>
        </nav>
      </header>

      <section className="landing-hero">
        <div className="landing-hero-copy">
          <p className="landing-eyebrow">
            Enterprise AI Agent Control Plane
          </p>

          <h1>
            Operate AI agents
            <span> from one platform.</span>
          </h1>

          <p className="landing-hero-description">
            Zevinq is building a self-service platform for engineering
            teams to register, version, deploy, govern, observe, and
            manage the operational lifecycle of AI agents.
          </p>

          <div className="landing-hero-actions">
            <Link
              to="/login"
              className="landing-primary-action"
            >
              Open Console
            </Link>

            <a
              href="#platform"
              className="landing-secondary-action"
            >
              Explore Platform
            </a>
          </div>

          <div className="landing-proof">
            <span>Multi-tenant workspaces</span>
            <span>Agent lifecycle</span>
            <span>Deployment governance</span>
            <span>AI usage visibility</span>
          </div>
        </div>

        <div className="landing-control-plane">
          <div className="control-plane-header">
            <div>
              <span className="control-plane-status" />
              Zevinq Control Plane
            </div>

            <span>Platform Online</span>
          </div>

          <div className="control-plane-stack">
            <div>
              <span>01</span>
              <strong>Workspace</strong>
              <small>Teams & projects</small>
            </div>

            <div>
              <span>02</span>
              <strong>Agent Registry</strong>
              <small>Identity & versions</small>
            </div>

            <div>
              <span>03</span>
              <strong>Deployment</strong>
              <small>Lifecycle & approvals</small>
            </div>

            <div>
              <span>04</span>
              <strong>Operations</strong>
              <small>Usage, governance & observability</small>
            </div>
          </div>
        </div>
      </section>

      <section
        id="platform"
        className="landing-section landing-platform"
      >
        <p className="landing-section-eyebrow">
          The Platform
        </p>

        <h2>
          A control plane for the operational side of AI.
        </h2>

        <p className="landing-section-copy">
          AI agents increasingly span models, prompts, tools,
          environments, infrastructure, policies, and providers.
          Zevinq brings those operational concerns into one
          engineering platform instead of scattering them across
          disconnected systems.
        </p>
      </section>

      <section
        id="capabilities"
        className="landing-section"
      >
        <div className="landing-section-heading">
          <div>
            <p className="landing-section-eyebrow">
              Capabilities
            </p>

            <h2>
              Built around the AI agent lifecycle.
            </h2>
          </div>

          <p>
            Zevinq is under active development as an early-stage
            platform, with capabilities being delivered incrementally.
          </p>
        </div>

        <div className="landing-capability-grid">
          {capabilities.map((capability) => (
            <article
              key={capability.title}
              className="landing-capability-card"
            >
              <span className="landing-capability-indicator" />

              <h3>{capability.title}</h3>

              <p>{capability.description}</p>
            </article>
          ))}
        </div>
      </section>

      <section
        id="architecture"
        className="landing-section landing-architecture"
      >
        <div>
          <p className="landing-section-eyebrow">
            Architecture
          </p>

          <h2>
            Designed as a platform, not a dashboard.
          </h2>

          <p>
            Zevinq separates the platform API, AI control plane,
            gateway, deployment controller, governance,
            observability, marketplace, and infrastructure layers
            so each responsibility can evolve independently.
          </p>
        </div>

        <div className="landing-architecture-flow">
          <span>Engineering Teams</span>
          <strong>↓</strong>
          <span>Zevinq Platform API</span>
          <strong>↓</strong>
          <span>AI Control Plane</span>
          <strong>↓</strong>
          <span>Runtime / Cloud / Kubernetes</span>
        </div>
      </section>

      <section className="landing-cta">
        <div>
          <p className="landing-section-eyebrow">
            Early Platform
          </p>

          <h2>
            Build the operational foundation for AI agents.
          </h2>
        </div>

        <Link
          to="/login"
          className="landing-primary-action"
        >
          Open Zevinq Console
        </Link>
      </section>

      <footer className="landing-footer">
        <div>
          <strong>Zevinq Labs</strong>
          <p>AI Platform Engineering</p>
        </div>

        <p>
          Building infrastructure for the AI agent lifecycle.
        </p>
      </footer>
    </main>
  );
}
