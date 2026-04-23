from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.home import home_route
from routes.auth import auth_route
from routes.users import user_route
from routes.balance import balance_route
from routes.predict import predict_route
from routes.history import history_route
from database.config import get_settings
from database.database import init_db
import uvicorn
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(home_route, tags=['Home'])
    app.include_router(user_route, prefix='/api/users', tags=['Users'])
    app.include_router(auth_route, prefix='/auth', tags=['Auth'])
    app.include_router(balance_route, prefix='/api/balance', tags=['Balance'])
    app.include_router(predict_route, prefix='/api/predict', tags=['ML Predictions'])
    app.include_router(history_route, prefix='/api/history', tags=['History'])

    return app

app = create_application()

@app.on_event("startup")
def on_startup():
    try:
        logger.info("Инициализация базы данных...")
        init_db()
        logger.info("Успешный запуск приложения")
    except Exception as e:
        logger.error(f"Ошибка при запуске: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка ресурсов при выключении"""
    logger.info("Остановка приложения...")

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run(
        'api:app',
        host='0.0.0.0',
        port=8080,
        reload=True,
        log_level="info"
    )