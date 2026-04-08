import uuid
import jwt as pyjwt
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.db import get_db, User
from backend.services.auth import hash_password, verify_password, create_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])


# ─── Pydantic request models ──────────────────────────────────────────────── #

class AuthRequest(BaseModel):
    username: str
    password: str


# ─── Auth dependency for protected routes ─────────────────────────────────── #

def get_current_user(authorization: str = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Chưa đăng nhập hoặc thiếu token")
    token = authorization[7:]
    try:
        payload = decode_token(token)
        return {"user_id": payload["sub"], "username": payload["username"]}
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token đã hết hạn, vui lòng đăng nhập lại")
    except Exception:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")


# ─── Endpoints ────────────────────────────────────────────────────────────── #

@router.post("/register")
def register(body: AuthRequest, db: Session = Depends(get_db)):
    if len(body.username.strip()) < 3:
        raise HTTPException(status_code=400, detail="Tên đăng nhập phải có ít nhất 3 ký tự")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Mật khẩu phải có ít nhất 6 ký tự")

    existing = db.query(User).filter(User.username == body.username.strip()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Tên đăng nhập đã tồn tại")

    user = User(
        id=str(uuid.uuid4()),
        username=body.username.strip().lower(),
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id, user.username)
    return {"token": token, "username": user.username, "user_id": user.id}


@router.post("/login")
def login(body: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username.strip().lower()).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Tên đăng nhập hoặc mật khẩu không đúng")

    token = create_token(user.id, user.username)
    return {"token": token, "username": user.username, "user_id": user.id}
