from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="BUAP DSS API",
    description="API for Decision Support System",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .routers import dashboard, predictions

print("Loading routers...")
app.include_router(dashboard.router)
app.include_router(predictions.router)
print("Routers loaded.")

@app.get("/")
def read_root():
    return {"message": "Welcome to BUAP DSS API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
