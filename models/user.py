from pydantic import BaseModel, Field

class UserModel(BaseModel):
    email: str
    password: str = Field(min_length=8)