const ACCESS_TOKEN_KEY = "zevinq.access_token";


export function getAccessToken(): string | null {
  return sessionStorage.getItem(ACCESS_TOKEN_KEY);
}


export function setAccessToken(
  accessToken: string,
): void {
  sessionStorage.setItem(
    ACCESS_TOKEN_KEY,
    accessToken,
  );
}


export function clearAccessToken(): void {
  sessionStorage.removeItem(
    ACCESS_TOKEN_KEY,
  );
}


export function hasAccessToken(): boolean {
  return getAccessToken() !== null;
}
