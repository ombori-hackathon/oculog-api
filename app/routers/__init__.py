from app.routers.condition_logs import router as condition_logs_router
from app.routers.weather import router as weather_router
from app.routers.auth import router as auth_router

__all__ = ["condition_logs_router", "weather_router", "auth_router"]
