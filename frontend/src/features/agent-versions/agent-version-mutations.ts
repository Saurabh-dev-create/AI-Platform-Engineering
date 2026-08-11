import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createAgentVersion,
  deprecateAgentVersion,
  publishAgentVersion,
  type CreateAgentVersionRequest,
} from "./agent-version-service";
import {
  agentVersionQueryKeys,
} from "./agent-version-queries";


interface CreateVersionVariables {
  agentId: string;
  version: CreateAgentVersionRequest;
}


export function useCreateAgentVersion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      agentId,
      version,
    }: CreateVersionVariables) =>
      createAgentVersion(
        agentId,
        version,
      ),

    onSuccess: async (_version, variables) => {
      await queryClient.invalidateQueries({
        queryKey:
          agentVersionQueryKeys.byAgent(
            variables.agentId,
          ),
      });
    },
  });
}


export function usePublishAgentVersion(
  agentId: string,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: publishAgentVersion,

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey:
          agentVersionQueryKeys.byAgent(agentId),
      });
    },
  });
}


export function useDeprecateAgentVersion(
  agentId: string,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deprecateAgentVersion,

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey:
          agentVersionQueryKeys.byAgent(agentId),
      });
    },
  });
}
