from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, TokenResponse, FirebaseLoginRequest
from passlib.context import CryptContext
from jose import jwt, JWTError
from slowapi import Limiter
from app.firebase_auth import verify_firebase_token
import os
from slowapi.util import get_remote_address
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

limiter = Limiter(key_func=get_remote_address)

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user



@router.post("/register", status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        hashed_password=hash_password(data.password),
        role=data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully", "user_id": user.id}



@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_token({"sub": str(user.id), "role": user.role})

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        role=user.role
    )

@router.post("/google-login", response_model=TokenResponse)
def google_login(data: FirebaseLoginRequest, db: Session = Depends(get_db)):
    """
    Accepts a Firebase ID token from frontend Google Sign-In.
    Verifies it with Firebase Admin SDK.
    Creates user in DB if first time, then returns our own JWT.
    """
    # Verify token with Firebase
    decoded = verify_firebase_token(data.id_token)
 
    email = decoded.get("email")
    name = decoded.get("name", email)
    picture = decoded.get("picture", "")
 
    if not email:
        raise HTTPException(status_code=400, detail="Email not found in token")
 
    # Check if user exists, create if not
    user = db.query(User).filter(User.email == email).first()
 
    if not user:
        # First time Google login — auto create account
        user = User(
            name=name,
            email=email,
            phone=None,
            hashed_password=hash_password(os.urandom(32).hex()),  # random password
            role="PATIENT"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
 
    # Issue our own JWT
    token = create_token({"sub": str(user.id), "role": user.role})
 
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        role=user.role
    )