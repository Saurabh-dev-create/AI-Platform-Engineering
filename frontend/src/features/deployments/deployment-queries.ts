import { useQuery } from "@tanstack/react-query";

import {
  listDeploymentsForVersion,
} from "./deployment-service";


export const deploymentQueryKeys = {
  all: ["deployments"] as const,

  byVersion: (versionId: string) =>
    [...deploymentQueryKeys.all, "version", versionId] as const,
};


export function useDeploymentsForVersion(
  versionId: string | null,
) {
  return useQuery({
    queryKey: versionId
      ? deploymentQueryKeys.byVersion(versionId)
      : deploymentQueryKeys.all,

    queryFn: () => {
      if (!versionId) {
        return Promise.resolve([]);
      }

      return listDeploymentsForVersion(versionId);
    },

    enabled: Boolean(versionId),
  });
}
