from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel

from .database import users

load_dotenv()

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserAuth(BaseModel):
    email: str
    password: str
    name: str | None = None


@router.post("/register")
async def register(user: UserAuth):
    email = user.email.lower()
    if await users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    await users.insert_one({
        "email": email,
        "password": pwd_context.hash(user.password),
        "name": user.name or email.split("@")[0],
    })
    return {
        "success": True,
        "email": email,
        "name": user.name or email.split("@")[0],
    }


@router.post("/login")
async def login(user: UserAuth):
    email = user.email.lower()
    db_user = await users.find_one({"email": email})

    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "success": True,
        "email": db_user["email"],
        "name": db_user.get("name", "User"),
    }
