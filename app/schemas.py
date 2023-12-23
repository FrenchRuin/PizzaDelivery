from pydantic import BaseModel, ConfigDict
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            'example': {
                'id': 0,
                'username': 'devLee',
                'email': 'devLee@gmail.com',
                "password": "password",
                "is_staff": False,
                "is_active": True
            }
        }
    )
