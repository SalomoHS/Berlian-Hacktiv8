from pydantic import BaseModel
from typing import Optional

class UserRequest(BaseModel):
    kota:Optional[str] = None

class UserResponse(BaseModel):
    id:int
    nama:str
    email:str
    kota:str
    jumlah_post:int

class UsersResponse(BaseModel):
    users:list[UserResponse]

class PostResponse(BaseModel):
    user_id:int
    nama:str
    posts:list[str]