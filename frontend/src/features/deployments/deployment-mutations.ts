import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createDeployment,
  transitionDeployment,
  type CreateDeploymentRequest,
  type TransitionDeploymentRequest,
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


interface TransitionDeploymentVariables {
  deploymentId: string;
  versionId: string;
  transition: TransitionDeploymentRequest;
}


export function useTransitionDeployment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      deploymentId,
      transition,
    }: TransitionDeploymentVariables) =>
      transitionDeployment(
        deploymentId,
        transition,
      ),

    onSuccess: async (_deployment, variables) => {
      await queryClient.invalidateQueries({
        queryKey:
          deploymentQueryKeys.byVersion(
            variables.versionId,
          ),
      });
    },
  });
}
