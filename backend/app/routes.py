from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.auth import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute("SELECT * FROM users WHERE username = :username", {"username": user.username})
    if existing_user.fetchone():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_pwd = hash_password(user.password)
    await db.execute("INSERT INTO users (username, hashed_password) VALUES (:username, :password)", 
                     {"username": user.username, "password": hashed_pwd})
    await db.commit()

    return UserResponse(id=1, username=user.username)

@router.post("/login")
async def login(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_record = await db.execute("SELECT * FROM users WHERE username = :username", {"username": user.username})
    user_record = user_record.fetchone()
    
    if not user_record or not verify_password(user.password, user_record.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
