"""FastAPI application entrypoint for Border Document Screening Platform."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import get_settings
from backend.app.logging import setup_logging
from backend.app.database import engine, Base
from backend.app.api.health import router as health_router
from backend.app.api.screenings import router as screenings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: setup logging and initialize tables if needed
    setup_logging()
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # If DB is temporarily unreachable at start, app still starts for health reporting
        pass
    yield
    # Shutdown: clean up if needed


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Decision-support platform for border identity document screening.",
    lifespan=lifespan,
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers under /api/v1
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(screenings_router, prefix="/api/v1", tags=["Screenings"])


@app.get("/", include_in_schema=False)
def root():
    return {
        "message": settings.APP_NAME,
        "docs": "/docs",
        "health": "/api/v1/health",
    }
