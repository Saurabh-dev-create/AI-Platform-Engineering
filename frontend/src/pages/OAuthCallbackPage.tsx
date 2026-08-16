import {
  useEffect,
  useRef,
  useState,
} from "react";
import {
  Link,
  useNavigate,
  useSearchParams,
} from "react-router-dom";

import {
  consumeOAuthHandoff,
  getCurrentUser,
  registerOAuthUser,
} from "../features/auth/auth-service";
import {
  clearAccessToken,
  setAccessToken,
} from "../features/auth/auth-session";
import { ApiError } from "../services/api-client";


type CallbackState =
  | "processing"
  | "error";


export function OAuthCallbackPage() {
  const navigate = useNavigate();

  const [searchParams] = useSearchParams();

  const startedRef = useRef(false);

  const [state, setState] =
    useState<CallbackState>("processing");

  const [message, setMessage] = useState(
    "Completing secure sign in...",
  );


  useEffect(() => {
    if (startedRef.current) {
      return;
    }

    startedRef.current = true;

    const code = searchParams.get("code");

    if (!code) {
      setState("error");
      setMessage(
        "The authentication response is missing its secure handoff code.",
      );

      return;
    }

    // Remove the one-time handoff code from the visible URL
    // before performing network work.
    window.history.replaceState(
      {},
      document.title,
      "/auth/oauth/callback",
    );

    async function completeOAuth() {
      clearAccessToken();

      try {
        const handoff =
          await consumeOAuthHandoff(code!);

        let tokens = handoff.tokens;

        if (
          handoff.status
          === "registration_required"
        ) {
          if (!handoff.continuation_token) {
            throw new Error(
              "OAuth registration continuation is missing",
            );
          }

          setMessage(
            "Creating your Zevinq Free workspace...",
          );

          const registration =
            await registerOAuthUser(
              handoff.continuation_token,
            );

          if (
            registration.status
              !== "authenticated"
            || !registration.tokens
          ) {
            throw new Error(
              "OAuth registration did not complete",
            );
          }

          tokens = registration.tokens;
        }

        if (
          handoff.status === "authenticated"
          && !tokens
        ) {
          throw new Error(
            "Authentication tokens are missing",
          );
        }

        if (!tokens) {
          throw new Error(
            "Authentication did not return a session",
          );
        }

        setMessage(
          "Verifying your Zevinq session...",
        );

        await getCurrentUser(
          tokens.access_token,
        );

        setAccessToken(
          tokens.access_token,
        );

        navigate(
          "/app/dashboard",
          {
            replace: true,
          },
        );
      } catch (error) {
        clearAccessToken();

        setState("error");

        if (error instanceof ApiError) {
          setMessage(error.message);
        } else {
          setMessage(
            "Unable to complete Google sign in. Please try again.",
          );
        }
      }
    }

    void completeOAuth();
  }, [
    navigate,
    searchParams,
  ]);


  return (
    <main className="oauth-callback-page">
      <section className="oauth-callback-card">
        <div className="login-brand-mark">
          Z
        </div>

        {state === "processing" ? (
          <>
            <div
              className="oauth-callback-spinner"
              aria-hidden="true"
            />

            <h1>
              Signing you in
            </h1>

            <p>
              {message}
            </p>

            <p className="oauth-callback-security">
              Secure OAuth session handoff in progress.
            </p>
          </>
        ) : (
          <>
            <h1>
              Sign in could not be completed
            </h1>

            <p
              className="login-error"
              role="alert"
            >
              {message}
            </p>

            <Link
              to="/login"
              className="oauth-callback-return"
            >
              Return to sign in
            </Link>
          </>
        )}
      </section>
    </main>
  );
}
