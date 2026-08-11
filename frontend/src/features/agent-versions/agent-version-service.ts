import { apiRequest } from "../../services/api-client";
import { getAccessToken } from "../auth/auth-session";


export type AgentVersionStatus =
  | "draft"
  | "published"
  | "deprecated";


export interface AgentVersion {
  id: string;
  agent_id: string;
  version_number: number;
  status: AgentVersionStatus;
  model_config: Record<string, unknown>;
  prompt_template: string | null;
  runtime_config: Record<string, unknown>;
  tool_config: Record<string, unknown>;
  change_summary: string | null;
  created_by_user_id: string | null;
  created_at: string;
  updated_at: string;
}


export interface CreateAgentVersionRequest {
  model_config: Record<string, unknown>;
  prompt_template: string | null;
  runtime_config: Record<string, unknown>;
  tool_config: Record<string, unknown>;
  change_summary: string | null;
}


function requireAccessToken(): string {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new Error("Authenticated session is required");
  }

  return accessToken;
}


export async function listAgentVersions(
  agentId: string,
): Promise<AgentVersion[]> {
  const accessToken = requireAccessToken();

  return apiRequest<AgentVersion[]>(
    `/agents/${agentId}/versions`,
    {
      method: "GET",
      accessToken,
    },
  );
}


export async function createAgentVersion(
  agentId: string,
  version: CreateAgentVersionRequest,
): Promise<AgentVersion> {
  const accessToken = requireAccessToken();

  return apiRequest<AgentVersion>(
    `/agents/${agentId}/versions`,
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(version),
    },
  );
}


export async function publishAgentVersion(
  versionId: string,
): Promise<AgentVersion> {
  const accessToken = requireAccessToken();

  return apiRequest<AgentVersion>(
    `/agent-versions/${versionId}/publish`,
    {
      method: "POST",
      accessToken,
    },
  );
}


export async function deprecateAgentVersion(
  versionId: string,
): Promise<AgentVersion> {
  const accessToken = requireAccessToken();

  return apiRequest<AgentVersion>(
    `/agent-versions/${versionId}/deprecate`,
    {
      method: "POST",
      accessToken,
    },
  );
}
