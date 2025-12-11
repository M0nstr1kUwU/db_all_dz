from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import User, get_db
from schemas import UserCreate, UserLogin, UserResponse, Token
import hashlib

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/register")
async def register(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username exists")

    hashed_pw = hash_password(password)
    new_user = User(username=username, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": f"User {username} created"}


@router.post("/login")
async def login(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    hashed_pw = hash_password(password)
    user = db.query(User).filter(
        User.username == username,
        User.password == hashed_pw
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": f"Welcome {username}", "user_id": user.id}


@router.get("/users", response_model=list[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/api/register")
async def api_register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username exists")

    hashed_pw = hash_password(user_data.password)
    new_user = User(username=user_data.username, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": f"User {user_data.username} created", "user_id": new_user.id}


@router.post("/api/login")
async def api_login(user_data: UserLogin, db: Session = Depends(get_db)):
    hashed_pw = hash_password(user_data.password)
    user = db.query(User).filter(
        User.username == user_data.username,
        User.password == hashed_pw
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": f"Welcome {user_data.username}", "user_id": user.id}