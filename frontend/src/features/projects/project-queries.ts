import { useQuery } from "@tanstack/react-query";

import { getProject, listProjects } from "./project-service";

export const projectQueryKeys = {
  all: ["projects"] as const,
  byWorkspace: (workspaceId: string) =>
    [...projectQueryKeys.all, "workspace", workspaceId] as const,

  detail: (projectId: string) =>
    [...projectQueryKeys.all, "detail", projectId] as const,
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


export function useProject(
  projectId: string | null,
) {
  return useQuery({
    queryKey: projectId
      ? projectQueryKeys.detail(projectId)
      : projectQueryKeys.all,

    queryFn: () => {
      if (!projectId) {
        throw new Error("Project ID is required");
      }

      return getProject(projectId);
    },

    enabled: Boolean(projectId),
  });
}
