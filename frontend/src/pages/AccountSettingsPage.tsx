import {
  useEffect,
  useMemo,
  useState,
} from "react";

import { GoogleIcon } from "../components/auth/GoogleIcon";
import {
  getCurrentUser,
  getLinkedIdentities,
  startGoogleLink,
  type CurrentUser,
  type LinkedIdentity,
} from "../features/auth/auth-service";
import {
  getAccessToken,
} from "../features/auth/auth-session";
import { ApiError } from "../services/api-client";


export function AccountSettingsPage() {
  const [user, setUser] =
    useState<CurrentUser | null>(null);

  const [identities, setIdentities] =
    useState<LinkedIdentity[]>([]);

  const [isLoading, setIsLoading] =
    useState(true);

  const [isConnecting, setIsConnecting] =
    useState(false);

  const [errorMessage, setErrorMessage] =
    useState<string | null>(null);


  useEffect(() => {
    async function loadAccount() {
      const accessToken = getAccessToken();

      if (!accessToken) {
        setErrorMessage(
          "Your Zevinq session is unavailable.",
        );
        setIsLoading(false);
        return;
      }

      try {
        const [
          currentUser,
          linkedIdentities,
        ] = await Promise.all([
          getCurrentUser(accessToken),
          getLinkedIdentities(accessToken),
        ]);

        setUser(currentUser);
        setIdentities(linkedIdentities);
      } catch (error) {
        if (error instanceof ApiError) {
          setErrorMessage(error.message);
        } else {
          setErrorMessage(
            "Unable to load account settings.",
          );
        }
      } finally {
        setIsLoading(false);
      }
    }

    void loadAccount();
  }, []);


  const googleIdentity = useMemo(
    () =>
      identities.find(
        (identity) =>
          identity.provider === "google",
      ) ?? null,
    [identities],
  );


  async function handleConnectGoogle() {
    const accessToken = getAccessToken();

    if (!accessToken) {
      setErrorMessage(
        "Your Zevinq session is unavailable.",
      );
      return;
    }

    setErrorMessage(null);
    setIsConnecting(true);

    try {
      await startGoogleLink(accessToken);
    } catch (error) {
      setIsConnecting(false);

      if (error instanceof ApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage(
          "Unable to start Google account linking.",
        );
      }
    }
  }


  if (isLoading) {
    return (
      <section className="account-settings-page">
        <p>Loading account settings...</p>
      </section>
    );
  }


  return (
    <section className="account-settings-page">
      <header className="account-settings-header">
        <div>
          <p className="account-settings-eyebrow">
            Profile
          </p>

          <h1>Account settings</h1>

          <p>
            Manage your Zevinq account and sign-in methods.
          </p>
        </div>
      </header>

      {errorMessage ? (
        <p
          className="login-error"
          role="alert"
        >
          {errorMessage}
        </p>
      ) : null}

      <div className="account-settings-grid">
        <section className="account-settings-card">
          <div className="account-settings-card-heading">
            <div>
              <h2>Personal information</h2>

              <p>
                Basic information associated with your
                Zevinq account.
              </p>
            </div>
          </div>

          <dl className="account-details">
            <div>
              <dt>Full name</dt>
              <dd>
                {user?.full_name || "Not available"}
              </dd>
            </div>

            <div>
              <dt>Email address</dt>
              <dd>
                {user?.email || "Not available"}
              </dd>
            </div>
          </dl>
        </section>

        <section className="account-settings-card">
          <div className="account-settings-card-heading">
            <div>
              <h2>Sign-in methods</h2>

              <p>
                Control how you authenticate to Zevinq.
              </p>
            </div>
          </div>

          <div className="signin-method-list">
            <div className="signin-method">
              <div>
                <div className="signin-method-title">
                  Password
                </div>

                <div className="signin-method-description">
                  Email and password authentication
                </div>
              </div>

              <span className="signin-method-badge">
                {user?.has_password
                  ? "Configured"
                  : "Not configured"}
              </span>
            </div>

            <div className="signin-method">
              <div className="signin-method-provider">
                <GoogleIcon />

                <div>
                  <div className="signin-method-title">
                    Google
                  </div>

                  <div className="signin-method-description">
                    {googleIdentity
                      ? (
                          googleIdentity.provider_email
                          || "Google account connected"
                        )
                      : "Connect your Google account"}
                  </div>
                </div>
              </div>

              {googleIdentity ? (
                <span className="signin-method-badge signin-method-connected">
                  Connected
                </span>
              ) : (
                <button
                  type="button"
                  className="account-connect-button"
                  onClick={handleConnectGoogle}
                  disabled={isConnecting}
                >
                  <GoogleIcon />

                  <span>
                    {isConnecting
                      ? "Connecting..."
                      : "Connect Google"}
                  </span>
                </button>
              )}
            </div>
          </div>
        </section>
      </div>
    </section>
  );
}
