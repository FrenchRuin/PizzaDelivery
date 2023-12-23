from pydantic import BaseModel, ConfigDict
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            'example': {
                'username': 'devLee',
                'email': 'devLee@gmail.com',
                "password": "password",
                "is_staff": False,
                "is_active": True
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = "3866635b4ab9ea251a6fc765f06123469cd91d5a9156eb66e8c0d305c553b1c4"


class LoginModel(BaseModel):
    username: str
    password: str
