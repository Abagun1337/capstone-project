from pydantic import BaseModel


class Token(BaseModel):            # Response body from /auth/token
    access_token: str
    token_type: str = 'bearer'


class TokenData(BaseModel):        # Decoded JWT payload
    email: str | None = None
    role: str | None = None
