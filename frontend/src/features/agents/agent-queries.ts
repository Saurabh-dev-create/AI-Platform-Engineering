import { useQuery } from "@tanstack/react-query";

import {
  getAgent,
  listAgents,
} from "./agent-service";


export const agentQueryKeys = {
  all: ["agents"] as const,

  byProject: (projectId: string) =>
    [...agentQueryKeys.all, "project", projectId] as const,

  detail: (agentId: string) =>
    [...agentQueryKeys.all, "detail", agentId] as const,
};


export function useAgents(
  projectId: string | null,
) {
  return useQuery({
    queryKey: projectId
      ? agentQueryKeys.byProject(projectId)
      : agentQueryKeys.all,

    queryFn: () => {
      if (!projectId) {
        return Promise.resolve([]);
      }

      return listAgents(projectId);
    },

    enabled: Boolean(projectId),
  });
}


export function useAgent(
  agentId: string | null,
) {
  return useQuery({
    queryKey: agentId
      ? agentQueryKeys.detail(agentId)
      : agentQueryKeys.all,

    queryFn: () => {
      if (!agentId) {
        throw new Error("Agent ID is required");
      }

      return getAgent(agentId);
    },

    enabled: Boolean(agentId),
  });
}
