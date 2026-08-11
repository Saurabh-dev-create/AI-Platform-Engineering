import { useQuery } from "@tanstack/react-query";

import {
  listAgentVersions,
} from "./agent-version-service";


export const agentVersionQueryKeys = {
  all: ["agent-versions"] as const,

  byAgent: (agentId: string) =>
    [...agentVersionQueryKeys.all, "agent", agentId] as const,
};


export function useAgentVersions(
  agentId: string | null,
) {
  return useQuery({
    queryKey: agentId
      ? agentVersionQueryKeys.byAgent(agentId)
      : agentVersionQueryKeys.all,

    queryFn: () => {
      if (!agentId) {
        return Promise.resolve([]);
      }

      return listAgentVersions(agentId);
    },

    enabled: Boolean(agentId),
  });
}
