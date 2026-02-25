from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username : str = Field(min_length=3)
    password : str = Field(min_length=6)

class UserResponse(BaseModel):
    id : int
    username : str

    class config:
        orm_mode = True

class LoginForm(BaseModel):
    username : str
    password : str

class ForgotPasswordRequest(BaseModel):
    username: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str