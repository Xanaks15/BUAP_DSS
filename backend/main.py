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

# Lista explícita + soporte para previews de Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://neskan.vercel.app",
        "https://neskan-q1rcvlpi4-xanaks15s-projects.vercel.app"
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Permite todos los subdominios de vercel.app (preview incluido)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers import dashboard, predictions

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
