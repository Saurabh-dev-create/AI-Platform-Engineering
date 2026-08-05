import {
  useEffect,
  useState,
} from "react";
import {
  Navigate,
  Outlet,
} from "react-router-dom";

import { getCurrentUser } from "./auth-service";
import {
  clearAccessToken,
  getAccessToken,
} from "./auth-session";

type SessionState =
  | "checking"
  | "authenticated"
  | "unauthenticated";

export function ProtectedRoute() {
  const [sessionState, setSessionState] =
    useState<SessionState>("checking");

  useEffect(() => {
    let isCancelled = false;

    async function validateSession() {
      const accessToken = getAccessToken();

      if (!accessToken) {
        if (!isCancelled) {
          setSessionState("unauthenticated");
        }

        return;
      }

      try {
        await getCurrentUser(accessToken);

        if (!isCancelled) {
          setSessionState("authenticated");
        }
      } catch {
        clearAccessToken();

        if (!isCancelled) {
          setSessionState("unauthenticated");
        }
      }
    }

    void validateSession();

    return () => {
      isCancelled = true;
    };
  }, []);

  if (sessionState === "checking") {
    return (
      <div className="app-session-loading">
        Verifying session...
      </div>
    );
  }

  if (sessionState === "unauthenticated") {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }

  return <Outlet />;
}
