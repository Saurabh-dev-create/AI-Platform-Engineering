import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createProject,
  type CreateProjectRequest,
} from "./project-service";
import { projectQueryKeys } from "./project-queries";

interface CreateProjectVariables {
  workspaceId: string;
  project: CreateProjectRequest;
}

export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      workspaceId,
      project,
    }: CreateProjectVariables) =>
      createProject(
        workspaceId,
        project,
      ),

    onSuccess: async (_project, variables) => {
      await queryClient.invalidateQueries({
        queryKey:
          projectQueryKeys.byWorkspace(
            variables.workspaceId,
          ),
      });
    },
  });
}
