
from pydantic import BaseModel, Field


class User(BaseModel):
    email: str = Field(..., description="email of the user") # TODO: use a real email class
    hashed_password: bytes = Field(..., description="password of the user")

    user_name: str | None = Field(default=None)
    discord: bool | None = Field(default=None)
    google: bool | None = Field(default=None)

    collection: list[int] = Field(default_factory=list, description="list of collected pet ids")

class UserCreateNative(BaseModel):
    email: str = Field(..., description="email of the user")
    password_plaintext: str

class UserOut(BaseModel):
    email: str = Field(..., description="email of the user")
    user_name: str | None = Field(default=None)
    discord: bool | None = Field(default=None)
    google: bool | None = Field(default=None)

    collection: list[int] = Field(default_factory=list, description="list of collected pet ids")