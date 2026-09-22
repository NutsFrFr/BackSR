import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .database import client

load_dotenv()

FRONTEND_URLS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_URL",
        "https://farmer-int-system-1wpmd6w52-null-pointers18.vercel.app",
    ).split(",")
    if origin.strip()
]
DB_NAME = os.getenv("DB_NAME", "farmer_int_db")

app = FastAPI(title="Farmer INT API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Backend is running", "database": DB_NAME}


@app.get("/health")
async def health():
    try:
        await client.admin.command("ping")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="MongoDB connection failed") from exc
    return {"status": "ok", "database": DB_NAME, "mongodb": "connected"}
