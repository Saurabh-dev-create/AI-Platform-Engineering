import {
  useState,
  type FormEvent,
} from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  getCurrentUser,
  login,
  startGoogleLogin,
} from "../features/auth/auth-service";
import {
  clearAccessToken,
  setAccessToken,
} from "../features/auth/auth-session";
import { ApiError } from "../services/api-client";


export function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setErrorMessage(null);
    setIsSubmitting(true);
    clearAccessToken();

    try {
      const tokens = await login({
        email: email.trim(),
        password,
      });

      await getCurrentUser(
        tokens.access_token,
      );

      setAccessToken(
        tokens.access_token,
      );

      setPassword("");

      navigate(
        "/app/dashboard",
        {
          replace: true,
        },
      );
    } catch (error) {
      clearAccessToken();
      setPassword("");

      if (error instanceof ApiError) {
        setErrorMessage(
          error.message,
        );
      } else {
        setErrorMessage(
          "Unable to sign in. Please try again.",
        );
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-visual">
        <div className="login-brand">
          <div className="login-brand-mark">
            Z
          </div>

          <div>
            <div className="login-brand-name">
              Zevinq
            </div>

            <div className="login-brand-subtitle">
              Labs
            </div>
          </div>
        </div>

        <div className="login-hero">
          <p className="login-eyebrow">
            AI Agent Control Plane
          </p>

          <h1>
            Operate AI agents
            <span> with confidence.</span>
          </h1>

          <p>
            Register, version, deploy, govern, and observe
            enterprise AI agents from one control plane.
          </p>

          <div className="login-capabilities">
            <div>
              <span className="capability-dot" />
              Agent Registry
            </div>

            <div>
              <span className="capability-dot" />
              Version Control
            </div>

            <div>
              <span className="capability-dot" />
              Deployment Governance
            </div>

            <div>
              <span className="capability-dot" />
              Token & Cost Visibility
            </div>
          </div>
        </div>

        <p className="login-footer-copy">
          Zevinq Labs · AI Platform Engineering
        </p>
      </section>

      <section className="login-form-section">
        <div className="login-card">
          <div className="login-card-heading">
            <p className="login-card-eyebrow">
              Welcome back
            </p>

            <h2>
              Sign in to Zevinq
            </h2>

            <p>
              Access your AI agent platform workspace.
            </p>
          </div>

          <button
            type="button"
            className="oauth-login-button"
            onClick={startGoogleLogin}
            disabled={isSubmitting}
          >
            Continue with Google
          </button>

          <div className="oauth-divider">
            <span>or continue with email</span>
          </div>

          <form
            className="login-form"
            onSubmit={handleSubmit}
          >
            <label>
              <span>Email address</span>

              <input
                type="email"
                name="email"
                placeholder="you@company.com"
                autoComplete="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                disabled={isSubmitting}
                required
              />
            </label>

            <label>
              <span>Password</span>

              <input
                type="password"
                name="password"
                placeholder="Enter your password"
                autoComplete="current-password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                disabled={isSubmitting}
                required
              />
            </label>

            <div className="login-form-meta">
              <span className="remember-field">
                Session-only authentication
              </span>

              <button
                type="button"
                className="forgot-password"
                disabled
              >
                Forgot password?
              </button>
            </div>

            {errorMessage ? (
              <p
                className="login-error"
                role="alert"
              >
                {errorMessage}
              </p>
            ) : null}

            <button
              type="submit"
              className="login-submit"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? "Signing in..."
                : "Sign in"}
            </button>
          </form>

          <div className="login-security-note">
            <span className="security-dot" />

            <span>
              Secure authentication powered by Zevinq Platform API
            </span>
          </div>

          <div className="login-security-note">
            <span>
              New to Zevinq?{" "}
              <Link to="/register">
                Create Free Account
              </Link>
            </span>
          </div>

        </div>
      </section>
    </main>
  );
}
