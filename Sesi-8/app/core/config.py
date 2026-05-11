from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    USER_API:str = os.getenv('USER_API')
    USER_POST_API:str = os.getenv('USER_POST_API') 

settings = Settings()