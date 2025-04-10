from pydantic import BaseModel
from typing import Optional, Union, List
from datetime import datetime, date

class tokenSettings(BaseModel):
    authjwt_secret_key: str = "26bd2796c4ad63ef29e96b73f320a996817857f9cf7f0c7fd6e90961d7c4bf58"

class signUpModel(BaseModel):
    id: Optional[int] = None
    username: str
    password: str
    first_name: str
    middle_name: str | None = None
    last_name: str
    email: str
    phone: str | None = None
    fax: str | None = None
    mobile: str
    other_contact: str | None = None
    workday_duration: int = 8
    hire_date: date | None = None
    release_date: date | None = None
    created: datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_enabled: bool = 1
    is_locked: bool = 0

    class Config:
        from_attributes = True

class loginModel(BaseModel):
    username: str  
    password: str

class userModel(BaseModel):
    id: Optional[int] = None
    username: str
    first_name: str
    middle_name: str | None = None
    last_name: str
    email: str
    phone: str | None = None
    fax: str | None = None
    mobile: str
    other_contact: str | None = None
    workday_duration: int = 8
    hire_date: date | None = None
    release_date: date | None = None
    created: datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_enabled: bool = 1
    is_locked: bool = 0
    access_token: str | None = None
    refresh_token: str | None = None

class userLoginResponse(BaseModel):
    status: int
    message: str
    data: userModel

class userSignUpResponse(BaseModel):
    status: int
    message: str
    data: userModel

class userAllResponse(BaseModel):
    status: int
    message: str
    data: list[userModel]


