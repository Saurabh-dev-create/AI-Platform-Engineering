import {
  useState,
  type FormEvent,
} from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import { GoogleIcon } from "../components/auth/GoogleIcon";
import {
  getCurrentUser,
  login,
  register,
  startGoogleLogin,
} from "../features/auth/auth-service";
import {
  clearAccessToken,
  setAccessToken,
} from "../features/auth/auth-session";
import { ApiError } from "../services/api-client";


export function RegisterPage() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] =
    useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] =
    useState(false);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setErrorMessage(null);
    setIsSubmitting(true);
    clearAccessToken();

    try {
      const normalizedEmail = email.trim();

      await register({
        full_name: fullName.trim(),
        email: normalizedEmail,
        password,
      });

      const tokens = await login({
        email: normalizedEmail,
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
        setErrorMessage(error.message);
      } else {
        setErrorMessage(
          "Unable to create your account. Please try again.",
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
            Start building
            <span> with Zevinq.</span>
          </h1>

          <p>
            Create your free workspace to register,
            manage, version, and govern AI agents.
          </p>

          <div className="login-capabilities">
            <div>
              <span className="capability-dot" />
              1 Workspace
            </div>

            <div>
              <span className="capability-dot" />
              Up to 2 Projects
            </div>

            <div>
              <span className="capability-dot" />
              Up to 3 AI Agents
            </div>

            <div>
              <span className="capability-dot" />
              No paid runtime usage
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
              Free workspace
            </p>

            <h2>
              Create your Zevinq account
            </h2>

            <p>
              Get started with the Zevinq AI Agent
              Control Plane.
            </p>
          </div>

          <button
            type="button"
            className="oauth-login-button"
            onClick={startGoogleLogin}
            disabled={isSubmitting}
          >
            <GoogleIcon />
            <span>Continue with Google</span>
          </button>

          <div className="oauth-divider">
            <span>or continue with email</span>
          </div>

          <form
            className="login-form"
            onSubmit={handleSubmit}
          >
            <label>
              <span>Full name</span>

              <input
                type="text"
                name="fullName"
                placeholder="Your name"
                autoComplete="name"
                value={fullName}
                onChange={(event) =>
                  setFullName(event.target.value)
                }
                disabled={isSubmitting}
                required
              />
            </label>

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
                placeholder="Create a password"
                autoComplete="new-password"
                minLength={8}
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                disabled={isSubmitting}
                required
              />
            </label>

            <p className="remember-field">
              Minimum 8 characters with at least
              one number and one special character.
            </p>

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
                ? "Creating workspace..."
                : "Create Free Account"}
            </button>
          </form>

          <div className="login-security-note">
            <span>
              Already have an account?{" "}
              <Link to="/login">
                Sign in
              </Link>
            </span>
          </div>
        </div>
      </section>
    </main>
  );
}
