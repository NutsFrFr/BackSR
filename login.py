from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from database import users

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Basic hashing

class UserAuth(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(user: UserAuth):
    # Check if email already exists
    if await users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Save to MongoDB
    await users.insert_one({
        "email": user.email,
        "password": pwd_context.hash(user.password), # Hash it so it's not plain text
        "name": user.email.split('@')[0] # Just use email prefix as name for prototype
    })
    return {"success": True, "email": user.email}

@router.post("/login")
async def login(user: UserAuth):
    db_user = await users.find_one({"email": user.email})
    
    # Check if user exists and password matches
    if not db_user or not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {"success": True, "email": db_user["email"], "name": db_user.get("name", "User")}