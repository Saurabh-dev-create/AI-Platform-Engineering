import { useQuery } from "@tanstack/react-query";

import { listWorkspaces } from "./workspace-service";

export const workspaceQueryKeys = {
  all: ["workspaces"] as const,
};

export function useWorkspaces() {
  return useQuery({
    queryKey: workspaceQueryKeys.all,
    queryFn: listWorkspaces,
  });
}
