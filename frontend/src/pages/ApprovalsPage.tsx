import { useState } from "react";

import { usePendingApprovals } from "../features/deployments/deployment-queries";
import { useTransitionDeployment } from "../features/deployments/deployment-mutations";
import { ApiError } from "../services/api-client";


export function ApprovalsPage() {
  const {
    data: approvals = [],
    isLoading,
    isError,
  } = usePendingApprovals();

  const transitionDeploymentMutation =
    useTransitionDeployment();

  const [approvalError, setApprovalError] =
    useState<string | null>(null);


  async function handleApprove(
    deploymentId: string,
    versionId: string,
  ) {
    setApprovalError(null);

    try {
      await transitionDeploymentMutation.mutateAsync({
        deploymentId,
        versionId,
        transition: {
          status: "approved",
        },
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setApprovalError(error.message);
      } else {
        setApprovalError(
          "Unable to approve deployment.",
        );
      }
    }
  }


  if (isLoading) {
    return (
      <section className="page-section">
        <p>Loading approvals...</p>
      </section>
    );
  }


  if (isError) {
    return (
      <section className="page-section">
        <p>Unable to load deployment approvals.</p>
      </section>
    );
  }


  return (
    <section className="page-section">
      <div className="page-heading">
        <div>
          <p className="page-eyebrow">
            Deployment Governance
          </p>

          <h1>Approvals</h1>

          <p>
            Review deployments waiting for administrative
            approval before they continue through the
            deployment lifecycle.
          </p>
        </div>
      </div>


      {approvalError ? (
        <p
          className="agent-version-form-error"
          role="alert"
        >
          {approvalError}
        </p>
      ) : null}


      {approvals.length === 0 ? (
        <div className="empty-state">
          <h2>No pending approvals</h2>

          <p>
            Deployment requests requiring approval
            will appear here.
          </p>
        </div>
      ) : (
        <div className="approval-grid">
          {approvals.map((deployment) => (
            <article
              key={deployment.id}
              className="project-card approval-card"
            >
              <div className="project-card-header">
                <div>
                  <p className="project-slug">
                    Deployment
                  </p>

                  <h2>
                    {deployment.environment}
                  </h2>
                </div>

                <span className="project-status">
                  {deployment.status}
                </span>
              </div>


              <div className="approval-detail-grid">
                <div>
                  <span>Strategy</span>
                  <strong>
                    {deployment.strategy}
                  </strong>
                </div>

                <div>
                  <span>Agent version</span>
                  <strong>
                    {deployment.agent_version_id}
                  </strong>
                </div>

                <div>
                  <span>Requested by</span>
                  <strong>
                    {deployment.requested_by_user_id
                      ?? "Unknown"}
                  </strong>
                </div>
              </div>


              <div className="agent-version-actions">
                <button
                  type="button"
                  className="topbar-button"
                  disabled={
                    transitionDeploymentMutation.isPending
                  }
                  onClick={() =>
                    void handleApprove(
                      deployment.id,
                      deployment.agent_version_id,
                    )
                  }
                >
                  {transitionDeploymentMutation.isPending
                    ? "Approving..."
                    : "Approve"}
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
