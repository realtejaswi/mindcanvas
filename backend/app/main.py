from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import auth, search, image, dashboard
from app.core.config import settings

app = FastAPI(
    title="MindCanvas API",
    description="AI-Powered Content & Image Explorer",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(image.router, prefix="/image", tags=["image"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    return {"message": "MindCanvas API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.environment}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)