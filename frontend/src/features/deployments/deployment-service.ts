import { apiRequest } from "../../services/api-client";
import { getAccessToken } from "../auth/auth-session";


export type DeploymentEnvironment =
  | "development"
  | "staging"
  | "production";


export type DeploymentStrategy =
  | "rolling"
  | "blue_green"
  | "canary";


export type DeploymentStatus =
  | "requested"
  | "pending_approval"
  | "approved"
  | "deploying"
  | "running"
  | "failed"
  | "terminated";


export interface Deployment {
  id: string;
  agent_version_id: string;
  environment: DeploymentEnvironment;
  strategy: DeploymentStrategy;
  status: DeploymentStatus;
  requested_by_user_id: string | null;
  failure_reason: string | null;
  created_at: string;
  updated_at: string;
}


export interface CreateDeploymentRequest {
  agent_version_id: string;
  environment: DeploymentEnvironment;
  strategy: DeploymentStrategy;
}


function requireAccessToken(): string {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new Error("Authenticated session is required");
  }

  return accessToken;
}


export async function createDeployment(
  deployment: CreateDeploymentRequest,
): Promise<Deployment> {
  const accessToken = requireAccessToken();

  return apiRequest<Deployment>(
    "/deployments",
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(deployment),
    },
  );
}


export async function listDeploymentsForVersion(
  versionId: string,
): Promise<Deployment[]> {
  const accessToken = requireAccessToken();

  return apiRequest<Deployment[]>(
    `/agent-versions/${versionId}/deployments`,
    {
      method: "GET",
      accessToken,
    },
  );
}


export interface TransitionDeploymentRequest {
  status: DeploymentStatus;
  failure_reason?: string | null;
}


export async function transitionDeployment(
  deploymentId: string,
  transition: TransitionDeploymentRequest,
): Promise<Deployment> {
  const accessToken = requireAccessToken();

  return apiRequest<Deployment>(
    `/deployments/${deploymentId}/transition`,
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(transition),
    },
  );
}


export async function listPendingApprovals(): Promise<Deployment[]> {
  const accessToken = requireAccessToken();

  return apiRequest<Deployment[]>(
    "/deployments/approvals",
    {
      method: "GET",
      accessToken,
    },
  );
}
