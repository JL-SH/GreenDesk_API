from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    full_name: str


class UserOut(UserCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
