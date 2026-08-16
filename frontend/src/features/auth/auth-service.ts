import { env } from "../../config/env";
import { apiRequest } from "../../services/api-client";


export interface LoginRequest {
  email: string;
  password: string;
}


export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}


export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_platform_admin: boolean;
  created_at: string;
  updated_at: string;
}


export async function login(
  credentials: LoginRequest,
): Promise<TokenResponse> {
  return apiRequest<TokenResponse>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify(credentials),
    },
  );
}


export async function getCurrentUser(
  accessToken: string,
): Promise<CurrentUser> {
  return apiRequest<CurrentUser>(
    "/auth/me",
    {
      method: "GET",
      accessToken,
    },
  );
}


export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}


export async function register(
  registration: RegisterRequest,
): Promise<CurrentUser> {
  return apiRequest<CurrentUser>(
    "/auth/register",
    {
      method: "POST",
      body: JSON.stringify(registration),
    },
  );
}


export function startGoogleLogin(): void {
  window.location.assign(
    `${env.apiBaseUrl}/auth/oauth/google/start`,
  );
}


export interface OAuthIdentityPreview {
  provider: string;
  email: string | null;
  email_verified: boolean;
  full_name: string | null;
  picture_url: string | null;
}


export interface OAuthHandoffResponse {
  status:
    | "authenticated"
    | "registration_required";

  tokens: TokenResponse | null;

  continuation_token: string | null;

  identity: OAuthIdentityPreview | null;
}


export async function consumeOAuthHandoff(
  code: string,
): Promise<OAuthHandoffResponse> {
  return apiRequest<OAuthHandoffResponse>(
    "/auth/oauth/handoff",
    {
      method: "POST",
      body: JSON.stringify({
        code,
      }),
    },
  );
}


export async function registerOAuthUser(
  continuationToken: string,
): Promise<OAuthHandoffResponse> {
  return apiRequest<OAuthHandoffResponse>(
    "/auth/oauth/register",
    {
      method: "POST",
      body: JSON.stringify({
        continuation_token:
          continuationToken,
      }),
    },
  );
}
