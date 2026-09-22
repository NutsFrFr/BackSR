from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from api.database import users

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserAuth(BaseModel):
    email: str
    password: str


@router.post("/register")
async def register(user: UserAuth):
    if await users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    await users.insert_one({
        "email": user.email,
        "password": pwd_context.hash(user.password),
        "name": user.email.split('@')[0],
    })
    return {"success": True, "email": user.email}


@router.post("/login")
async def login(user: UserAuth):
    db_user = await users.find_one({"email": user.email})

    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"success": True, "email": db_user["email"], "name": db_user.get("name", "User")}
