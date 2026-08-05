import { Navigate, createBrowserRouter } from "react-router-dom";

import { AppLayout } from "../layouts/AppLayout";
import { DashboardPage } from "../pages/DashboardPage";
import { LoginPage } from "../pages/LoginPage";

import {
  AgentsPage,
  ApprovalsPage,
  DeploymentsPage,
  GovernancePage,
  LandingPage,
  MarketplacePage,
  NotFoundPage,
  ObservabilityPage,
  ProjectsPage,
  UsagePage,
} from "../pages/PlaceholderPages";


export const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage />,
  },
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/app",
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/app/dashboard" replace />,
      },
      {
        path: "dashboard",
        element: <DashboardPage />,
      },
      {
        path: "projects",
        element: <ProjectsPage />,
      },
      {
        path: "agents",
        element: <AgentsPage />,
      },
      {
        path: "deployments",
        element: <DeploymentsPage />,
      },
      {
        path: "approvals",
        element: <ApprovalsPage />,
      },
      {
        path: "usage",
        element: <UsagePage />,
      },
      {
        path: "observability",
        element: <ObservabilityPage />,
      },
      {
        path: "governance",
        element: <GovernancePage />,
      },
      {
        path: "marketplace",
        element: <MarketplacePage />,
      },
    ],
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);
