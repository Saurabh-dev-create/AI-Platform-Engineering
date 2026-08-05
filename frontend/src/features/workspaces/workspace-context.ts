import { createContext } from "react";

import type { Workspace } from "./workspace-service";

export interface WorkspaceContextValue {
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  isLoading: boolean;
  isError: boolean;
  setCurrentWorkspaceId: (workspaceId: string) => void;
}

export const WorkspaceContext =
  createContext<WorkspaceContextValue | null>(null);
