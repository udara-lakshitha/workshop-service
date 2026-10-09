from fastapi import FastAPI
from app.database import Base,engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Workshop Registration Service")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:5173"],
    allow_headers = ["*"],
    allow_methods = ["*"],
)

@app.get("/")
def root():
    return { "message": "backend is running" }