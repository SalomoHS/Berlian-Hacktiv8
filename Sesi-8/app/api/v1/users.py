from fastapi import APIRouter, Depends, Request
from services.users import User
from models.models import UserRequest, UserResponse, PostResponse
from typing import Optional
router = APIRouter()

def get_user_service(request: Request):
    return User(request)

@router.get("/users", response_model = list[UserResponse])
def get_users_summary(user_request:UserRequest, user:User = Depends(get_user_service)) -> list[dict]:
    """
    Melakukan pencarian user detail.
    Arg:
        kota (optional[str]): Dapat difilter berdasarkan kota.
                              Default to None
    Return:
        list[dict]: User detail summary
    """
    users = user.get_user_summary(user_request)
    return users

@router.get("/users/{user_id}/posts", response_model = PostResponse)
def get_user_posts(user_id:int, user:User = Depends(get_user_service)):
    """
    Melakukan pencarian post dari user.
    Arg:
        user_id (int): User id.
    Return:
        dict: User post detail. { 'user_id':str, 'nama':str, 'posts':[] }
    """
    list_post_title = user.get_user_posts(user_id)
    return list_post_title