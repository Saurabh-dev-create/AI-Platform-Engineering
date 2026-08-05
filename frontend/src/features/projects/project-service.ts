import { apiRequest } from "../../services/api-client";
import { getAccessToken } from "../auth/auth-session";

export interface Project {
  id: string;
  team_id: string;
  name: string;
  slug: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectRequest {
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

export async function listProjects(
  workspaceId: string,
): Promise<Project[]> {
  const accessToken = requireAccessToken();

  return apiRequest<Project[]>(
    `/teams/${workspaceId}/projects`,
    {
      method: "GET",
      accessToken,
    },
  );
}

export async function createProject(
  workspaceId: string,
  project: CreateProjectRequest,
): Promise<Project> {
  const accessToken = requireAccessToken();

  return apiRequest<Project>(
    `/teams/${workspaceId}/projects`,
    {
      method: "POST",
      accessToken,
      body: JSON.stringify(project),
    },
  );
}
