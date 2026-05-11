import requests
from fastapi import Request
from core.config import settings
from models.models import UserRequest
from fastapi import HTTPException

class User:
    def __init__(self, request:Request) -> None:
        self.user_summary = request.app.state.user_summary

    def get_user_by_city(self, kota:str):
        """
        Melakukan pencarian user detail berdasarkan kota.
        Arg:
            kota (str): Nama kota.
        Return:
            list[dict]: User di kota tersebut.
        """
        found = []
        for i in self.user_summary:
                if i['kota'] == kota:
                    found.append(i)
        return found

    def get_user_summary(self, user_request:UserRequest) -> list[dict]:
        """
        Melakukan pencarian user detail.
        Arg:
            kota (optional[str]): Nama kota.
        Return:
            list[dict]: User detail summary.
        """
        if user_request.kota:
            return self.get_user_by_city(user_request.kota)
        
        return self.user_summary
    
    def get_user_name(self, user_id:int) -> str:
        """
        Melakukan pencarian nama user berdasarkan user id.
        Arg:
            user_id (int): user id.
        Return:
            str: Nama user.
        """
        for i in self.user_summary:
            if i["id"] == user_id:
                return i["nama"]
    
    def get_user_posts(self, user_id:int) -> dict:
        """
        Melakukan pencarian post berdasarkan user id.
        Arg:
            user_id (int): user id.
        Return:
            dict: Post detail.
        """
        response = requests.get(settings.USER_POST_API + f"?userId={user_id}")
        if len(response.json()) == 0:
             raise HTTPException(status_code=404, detail="User tidak ditemukan")

        temp = {
            "user_id": user_id,
            "nama": self.get_user_name(user_id),
            "posts": [i['title'] for i in response.json()]
        }

        return temp