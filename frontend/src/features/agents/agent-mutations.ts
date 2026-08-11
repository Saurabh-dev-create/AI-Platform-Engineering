import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createAgent,
  type CreateAgentRequest,
} from "./agent-service";
import { agentQueryKeys } from "./agent-queries";


interface CreateAgentVariables {
  projectId: string;
  agent: CreateAgentRequest;
}


export function useCreateAgent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      projectId,
      agent,
    }: CreateAgentVariables) =>
      createAgent(
        projectId,
        agent,
      ),

    onSuccess: async (_agent, variables) => {
      await queryClient.invalidateQueries({
        queryKey:
          agentQueryKeys.byProject(
            variables.projectId,
          ),
      });
    },
  });
}
