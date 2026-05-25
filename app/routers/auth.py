from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest, LoginRequest, RefreshRequest,
    UserOut, TokenData, AccessTokenData,
    UpdateProfileRequest, ChangePasswordRequest
)
from app.services.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return authorization.split(" ")[1]

@router.post("/register", status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=422, detail={
            "message": "Validation failed", "code": 422,
            "errors": [{"field": "email", "issue": "email already registered"}]
        })
    user = User(name=body.name, email=body.email, hashed_password=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"status": "success", "data": UserOut.model_validate(user)}

@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail={"message": "Invalid email or password", "code": 401})
    return {
        "status": "success",
        "data": {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
            "expires_in": 3600,
            "user": UserOut.model_validate(user)
        }
    }

@router.post("/logout")
def logout(token: str = Depends(get_token)):
    return {"status": "success", "message": "Logged out successfully"}

@router.post("/refresh")
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError()
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail={"message": "Refresh token expired, please login again", "code": 401})

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail={"message": "User not found", "code": 401})

    return {
        "status": "success",
        "data": {"access_token": create_access_token(user.id), "expires_in": 3600}
    }

@router.get("/me")
def get_me(token: str = Depends(get_token), db: Session = Depends(get_db)):
    try:
        user = get_current_user(token, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail={"message": str(e), "code": 401})
    return {"status": "success", "data": UserOut.model_validate(user)}

@router.patch("/me")
def update_me(body: UpdateProfileRequest, token: str = Depends(get_token), db: Session = Depends(get_db)):
    try:
        user = get_current_user(token, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail={"message": str(e), "code": 401})

    if body.name:
        user.name = body.name
    if body.email:
        existing = db.query(User).filter(User.email == body.email, User.id != user.id).first()
        if existing:
            raise HTTPException(status_code=422, detail={"message": "Email already in use", "code": 422})
        user.email = body.email

    db.commit()
    db.refresh(user)
    return {"status": "success", "data": UserOut.model_validate(user)}

@router.patch("/me/password")
def change_password(body: ChangePasswordRequest, token: str = Depends(get_token), db: Session = Depends(get_db)):
    try:
        user = get_current_user(token, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail={"message": str(e), "code": 401})

    if not verify_password(body.current_password, user.hashed_password):
        raise HTTPException(status_code=422, detail={"message": "Current password is incorrect", "code": 422})

    user.hashed_password = hash_password(body.new_password)
    db.commit()
    return {"status": "success", "message": "Password updated successfully"}
