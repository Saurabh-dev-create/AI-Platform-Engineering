import {
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { WorkspaceContext } from "./workspace-context";
import { useWorkspaces } from "./workspace-queries";

interface WorkspaceProviderProps {
  children: ReactNode;
}

export function WorkspaceProvider({
  children,
}: WorkspaceProviderProps) {
  const {
    data: workspaces = [],
    isLoading,
    isError,
  } = useWorkspaces();

  const [
    selectedWorkspaceId,
    setSelectedWorkspaceId,
  ] = useState<string | null>(null);

  const currentWorkspace = useMemo(() => {
    if (workspaces.length === 0) {
      return null;
    }

    return (
      workspaces.find(
        (workspace) =>
          workspace.id === selectedWorkspaceId,
      )
      ?? workspaces[0]
    );
  }, [
    workspaces,
    selectedWorkspaceId,
  ]);

  const value = useMemo(
    () => ({
      workspaces,
      currentWorkspace,
      isLoading,
      isError,
      setCurrentWorkspaceId: setSelectedWorkspaceId,
    }),
    [
      workspaces,
      currentWorkspace,
      isLoading,
      isError,
    ],
  );

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
}
