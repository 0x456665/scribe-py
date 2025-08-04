# from fastapi import FastAPI
# import whisper

# def main():
#     model = whisper.load_model("base")
#     result = model.transcribe("/home/efemena/Downloads/Model_test_1.m4a")
#     print(result["text"])


# if __name__ == "__main__":
#     main()


from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import os
import sys
from config.settings import settings
from routes.auth import auth_router
from routes.transcription import transcription_router
from errors.custom_exceptions import CustomException
from models import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AI Scribe API...")

    # Create upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Create database tables
    await create_db_and_tables()

    logger.info("AI Scribe API started successfully")
    yield

    # Shutdown
    logger.info("Shutting down AI Scribe API...")


# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO" if not settings.DEBUG else "DEBUG")

# Create FastAPI app
app = FastAPI(
    title="AI Scribe API",
    description="AI-powered transcription service",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000" ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(transcription_router, prefix=settings.API_V1_PREFIX)


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    """Handle custom exceptions"""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Scribe API"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to AI Scribe API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
