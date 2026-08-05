import { apiRequest } from "../../services/api-client";
import { getAccessToken } from "../auth/auth-session";

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export async function listWorkspaces(): Promise<Workspace[]> {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new Error("Authenticated session is required");
  }

  return apiRequest<Workspace[]>(
    "/teams",
    {
      method: "GET",
      accessToken,
    },
  );
}
