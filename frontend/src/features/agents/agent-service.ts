import { apiRequest } from "../../services/api-client";
import { getAccessToken } from "../auth/auth-session";


export type AgentStatus =
  | "draft"
  | "active"
  | "archived";


export interface Agent {
  id: string;
  project_id: string;
  name: string;
  slug: string;
  description: string | null;
  status: AgentStatus;
  created_at: string;
  updated_at: string;
}


export interface CreateAgentRequest {
  name: string;
  slug: string;
  description: string | null;
}


function requireAccessToken(): string {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new Error("Authenticated session is required");
  }

  return accessToken;
}


export async function listAgents(
  projectId: string,
): Promise<Agent[]> {
  const accessToken = requireAccessToken();

  return apiRequest<Agent[]>(
    `/projects/${projectId}/agents`,
    {
      method: "GET",
      accessToken,
    },
  );
}


export async function getAgent(
  agentId: string,
): Promise<Agent> {
  const accessToken = requireAccessToken();

  return apiRequest<Agent>(
    `/agents/${agentId}`,
    {
      method: "GET",
      accessToken,
    },
  );
}


export async function createAgent(
  projectId: string,
  agent: CreateAgentRequest,
): Promise<Agent> {
  const accessToken = requireAccessToken();

  return apiRequest<Agent>(
    `/projects/${projectId}/agents`,
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(agent),
    },
  );
}
