import type { ReactNode } from "react";

import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";

import { WorkspaceProvider } from "../features/workspaces/WorkspaceProvider";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

interface AppProvidersProps {
  children: ReactNode;
}

export function AppProviders({
  children,
}: AppProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <WorkspaceProvider>
        {children}
      </WorkspaceProvider>
    </QueryClientProvider>
  );
}
