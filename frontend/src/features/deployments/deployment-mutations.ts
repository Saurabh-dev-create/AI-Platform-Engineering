import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createDeployment,
  type CreateDeploymentRequest,
} from "./deployment-service";
import {
  deploymentQueryKeys,
} from "./deployment-queries";


export function useCreateDeployment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (
      deployment: CreateDeploymentRequest,
    ) => createDeployment(deployment),

    onSuccess: async (deployment) => {
      await queryClient.invalidateQueries({
        queryKey:
          deploymentQueryKeys.byVersion(
            deployment.agent_version_id,
          ),
      });
    },
  });
}
