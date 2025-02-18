from fastapi import Depends, HTTPException, status
import jwt
from app.config import settings
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.schemas import UserResponse

async def get_current_user(token: str, db: AsyncSession = Depends(get_db)) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.execute("SELECT * FROM users WHERE username = :username", {"username": username})
    user = user.fetchone()
    if user is None:
        raise credentials_exception

    return UserResponse(id=user.id, username=user.username)
