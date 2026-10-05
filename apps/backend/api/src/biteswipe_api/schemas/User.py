from pydantic import BaseModel


class UserResponse(BaseModel):
    uid: str
    email: str | None = None
    displayName: str | None = None