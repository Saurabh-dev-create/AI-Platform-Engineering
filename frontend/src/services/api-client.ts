import { env } from "../config/env";


interface ApiErrorPayload {
  error?: {
    code?: string;
    message?: string;
    details?: Record<string, unknown>;
    correlation_id?: string;
  };
}


export class ApiError extends Error {
  readonly status: number;
  readonly code: string | null;
  readonly correlationId: string | null;
  readonly details: Record<string, unknown>;

  constructor(
    message: string,
    options: {
      status: number;
      code?: string | null;
      correlationId?: string | null;
      details?: Record<string, unknown>;
    },
  ) {
    super(message);

    this.name = "ApiError";
    this.status = options.status;
    this.code = options.code ?? null;
    this.correlationId = options.correlationId ?? null;
    this.details = options.details ?? {};
  }
}


interface ApiRequestOptions extends RequestInit {
  accessToken?: string;
}


export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const {
    accessToken,
    headers,
    ...requestOptions
  } = options;

  const response = await fetch(
    `${env.apiBaseUrl}${path}`,
    {
      ...requestOptions,
      headers: {
        "Content-Type": "application/json",
        ...headers,
        ...(accessToken
          ? {
              Authorization: `Bearer ${accessToken}`,
            }
          : {}),
      },
    },
  );

  if (!response.ok) {
    let payload: ApiErrorPayload | undefined;

    try {
      payload = await response.json();
    } catch {
      payload = undefined;
    }

    throw new ApiError(
      payload?.error?.message
        ?? `Request failed with status ${response.status}`,
      {
        status: response.status,
        code: payload?.error?.code ?? null,
        correlationId:
          payload?.error?.correlation_id ?? null,
        details: payload?.error?.details ?? {},
      },
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
