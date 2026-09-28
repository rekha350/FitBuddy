from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from app.database import init_db

from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create SQLite tables when the application starts.
    init_db()

    yield


app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",

    description=(
        "AI-powered personalized 7-day workout plans, "
        "nutrition tips, and feedback-based plan updates."
    ),

    version="1.0.0",

    lifespan=lifespan,
)


app.mount(
    "/static",

    StaticFiles(
        directory="app/static"
    ),

    name="static",
)


app.include_router(
    router
)