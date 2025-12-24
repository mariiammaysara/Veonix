from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.routers.analyze import router as analyze_router
from app.core.routers.health import router as health_router
from app.core.database import engine, Base
from app.models import meal

def create_app() -> FastAPI:
    settings = get_settings()
    Base.metadata.create_all(bind=engine)

    application = FastAPI( 
        title=settings.app_name,
        debug=settings.debug,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health_router)
    application.include_router(analyze_router)

    return application

app = create_app()