from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )
    full_name: str = Field(
        min_length=1,
        max_length=255,
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not any(character.isdigit() for character in password):
            raise ValueError(
                "Password must contain at least one digit"
            )

        if not any(
            not character.isalnum()
            for character in password
        ):
            raise ValueError(
                "Password must contain at least one "
                "special character"
            )

        return password


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=1,
        max_length=128,
    )


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthenticatedIdentityResponse(BaseModel):
    user_id: str
    token_id: str
