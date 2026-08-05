import { useQuery } from "@tanstack/react-query";

import { listProjects } from "./project-service";

export const projectQueryKeys = {
  all: ["projects"] as const,
  byWorkspace: (workspaceId: string) =>
    [...projectQueryKeys.all, workspaceId] as const,
};

export function useProjects(
  workspaceId: string | null,
) {
  return useQuery({
    queryKey: workspaceId
      ? projectQueryKeys.byWorkspace(workspaceId)
      : projectQueryKeys.all,
    queryFn: () => {
      if (!workspaceId) {
        return Promise.resolve([]);
      }

      return listProjects(workspaceId);
    },
    enabled: Boolean(workspaceId),
  });
}
