import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.database.connection import engine, Base, SessionLocal
from backend.app.database.seed_data import seed_database
from backend.app.api.endpoints import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database schema exists and seed data is populated
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    # Shutdown logic if any

app = FastAPI(
    title="USAR SPACE AI — Smart Classroom Availability & Timetable Analysis System",
    description="Full-stack real-time college classroom availability calculation and timetable analytics engine.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

# Mount uploads dir if exists
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def root():
    return {
        "system": "USAR SPACE AI",
        "version": "1.0.0",
        "campus": "University School of Automation and Robotics (USAR)",
        "timezone": "IST (Asia/Kolkata)",
        "status": "Operational",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
