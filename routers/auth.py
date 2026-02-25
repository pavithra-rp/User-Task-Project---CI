from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, LoginForm, ForgotPasswordRequest, ResetPasswordRequest
from utils.jwt import create_access_token, create_reset_token
from utils.security import hash_password, verify_password
from deps import get_db
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM="HS256"

router = APIRouter(prefix="/auth", tags=["Auth"])

# New User 
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user= db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user=User(
        username= user.username,
        password= hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "User added successfully.."}

# Existing User
@router.post("/login")
def login(response: Response, form_data: LoginForm, db: Session= Depends(get_db)):
    user=db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    token = create_access_token({"user_id": user.id})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,   # True in production (HTTPS)
        samesite="lax"
    )
    return {"message": "Login success"}
 
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

# Generate token for updating another password
@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_reset_token(data.username)

    return {
        "reset_token": token,
        "message": "token to reset password"
    }

# Reset Password
def verify_reset_token(token : str):
    try:
    
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("purpose") != "reset_password":
            raise HTTPException(status_code=400, detail="Invalid token purpose")

        return payload.get("sub")

    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest ,db: Session = Depends(get_db)):
    username = verify_reset_token(data.token)
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = hash_password(data.new_password)
    db.commit()

    return {"message": "Password reset successful..."}