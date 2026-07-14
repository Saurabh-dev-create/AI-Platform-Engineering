from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthenticatedIdentityResponse(BaseModel):
    user_id: str
    token_id: str
