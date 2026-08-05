const summaryCards = [
  {
    label: "Total Agents",
    value: "12",
    detail: "+2 this week",
  },
  {
    label: "Running Deployments",
    value: "8",
    detail: "+1 this week",
  },
  {
    label: "Token Usage",
    value: "2.41M",
    detail: "+18.4% vs last 7 days",
  },
  {
    label: "Monthly Cost",
    value: "$184.62",
    detail: "-9.3% vs last month",
  },
];


const deployments = [
  {
    agent: "Customer Support Agent",
    version: "v2",
    environment: "Staging",
    strategy: "Canary",
    status: "Running",
  },
  {
    agent: "RCA Agent",
    version: "v7",
    environment: "Production",
    strategy: "Blue/Green",
    status: "Running",
  },
  {
    agent: "Data Analyst Agent",
    version: "v3",
    environment: "Development",
    strategy: "Rolling",
    status: "Running",
  },
  {
    agent: "Finance Agent",
    version: "v2",
    environment: "Production",
    strategy: "Canary",
    status: "Pending Approval",
  },
];


const approvals = [
  {
    title: "Deploy v3 of Legal Agent",
    environment: "Production",
    age: "2m ago",
  },
  {
    title: "Deploy v2 of Sales Agent",
    environment: "Staging",
    age: "15m ago",
  },
  {
    title: "Model change in Support Agent",
    environment: "Production",
    age: "1h ago",
  },
];


const systemServices = [
  "Platform API",
  "Database",
  "Redis",
  "AI Gateway",
  "GitOps Sync",
  "Argo CD",
];


export function DashboardPage() {
  return (
    <section className="dashboard">
      <div className="dashboard-heading">
        <div>
          <p className="dashboard-eyebrow">Platform overview</p>
          <h1>Good morning</h1>
          <p className="dashboard-subtitle">
            Here&apos;s what&apos;s happening with your AI agents today.
          </p>
        </div>

        <button
          type="button"
          className="dashboard-range-button"
        >
          Last 7 days
        </button>
      </div>

      <div className="summary-grid">
        {summaryCards.map((card) => (
          <article
            key={card.label}
            className="summary-card"
          >
            <p className="summary-card-label">
              {card.label}
            </p>

            <p className="summary-card-value">
              {card.value}
            </p>

            <p className="summary-card-detail">
              {card.detail}
            </p>
          </article>
        ))}
      </div>

      <div className="dashboard-grid dashboard-grid-primary">
        <section className="dashboard-panel dashboard-panel-wide">
          <div className="panel-heading">
            <div>
              <p className="panel-title">
                Recent Deployments
              </p>
              <p className="panel-subtitle">
                Latest agent rollout activity
              </p>
            </div>

            <button
              type="button"
              className="panel-link"
            >
              View all
            </button>
          </div>

          <div className="deployment-table">
            <div className="deployment-row deployment-row-header">
              <span>Agent</span>
              <span>Version</span>
              <span>Environment</span>
              <span>Strategy</span>
              <span>Status</span>
            </div>

            {deployments.map((deployment) => (
              <div
                key={`${deployment.agent}-${deployment.environment}`}
                className="deployment-row"
              >
                <span className="deployment-agent">
                  {deployment.agent}
                </span>

                <span>{deployment.version}</span>
                <span>{deployment.environment}</span>
                <span>{deployment.strategy}</span>

                <span>
                  <span
                    className={
                      deployment.status === "Running"
                        ? "status-badge status-running"
                        : "status-badge status-pending"
                    }
                  >
                    {deployment.status}
                  </span>
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-title">
                Token Usage
              </p>
              <p className="panel-subtitle">
                Across all agents
              </p>
            </div>
          </div>

          <div className="metric-feature">
            <div>
              <p className="metric-feature-value">
                2.41M
              </p>
              <p className="metric-feature-label">
                tokens
              </p>
            </div>

            <p className="metric-feature-change">
              +18.4%
            </p>
          </div>

          <div className="usage-chart-placeholder">
            <div className="usage-chart-line" />
          </div>

          <div className="usage-chart-axis">
            <span>Jul 30</span>
            <span>Aug 1</span>
            <span>Aug 3</span>
            <span>Aug 5</span>
          </div>
        </section>
      </div>

      <div className="dashboard-grid dashboard-grid-secondary">
        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-title">
                Monthly Cost
              </p>
              <p className="panel-subtitle">
                Estimated LLM spend
              </p>
            </div>
          </div>

          <p className="cost-value">
            $184.62
          </p>

          <div className="cost-bars">
            {[34, 42, 29, 57, 48, 70, 53, 82, 64, 76, 58, 88].map(
              (height, index) => (
                <span
                  key={index}
                  style={{ height: `${height}%` }}
                />
              ),
            )}
          </div>
        </section>

        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-title">
                Approvals
              </p>
              <p className="panel-subtitle">
                Requests requiring action
              </p>
            </div>

            <span className="approval-count">
              {approvals.length}
            </span>
          </div>

          <div className="approval-list">
            {approvals.map((approval) => (
              <div
                key={approval.title}
                className="approval-item"
              >
                <div>
                  <p className="approval-title">
                    {approval.title}
                  </p>
                  <p className="approval-meta">
                    {approval.environment}
                  </p>
                </div>

                <span className="approval-age">
                  {approval.age}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="dashboard-panel system-panel">
        <div className="panel-heading">
          <div>
            <p className="panel-title">
              System Status
            </p>
            <p className="panel-subtitle">
              Zevinq platform components
            </p>
          </div>
        </div>

        <div className="system-status-grid">
          {systemServices.map((service) => (
            <div
              key={service}
              className="system-service"
            >
              <span className="system-service-dot" />

              <div>
                <p>{service}</p>
                <span>Healthy</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </section>
  );
}
