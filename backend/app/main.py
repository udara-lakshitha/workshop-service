from fastapi import FastAPI
from app.database import Base,engine
from app import models
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, registrations, workshops
from seed import seed

app = FastAPI(title="Workshop Registration Service")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_headers = ["*"],
    allow_methods = ["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(workshops.router)
app.include_router(registrations.router)

@app.get("/")
def root():
    seed()
    return { "message": "backend is running" }