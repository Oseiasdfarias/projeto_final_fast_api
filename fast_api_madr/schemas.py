from pydantic import BaseModel, ConfigDict, EmailStr


class Message(BaseModel):
    message: str


class AccountSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class AccountPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class AccountList(BaseModel):
    accounts: list[AccountPublic]


class Token(BaseModel):
    access_token: str
    token_type: str
