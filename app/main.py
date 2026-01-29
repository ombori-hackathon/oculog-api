from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.exceptions import AppException
from app.routers import condition_logs_router, weather_router, auth_router

app = FastAPI(
    title="Oculog API",
    description="Eye condition tracking API for dry eye disease and MGD",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(condition_logs_router)
app.include_router(weather_router)
app.include_router(auth_router)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": exc.error_type.value,
            "message": exc.message,
            "data": exc.data,
        },
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert Pydantic validation errors to unified format"""
    field_errors = {}
    for error in exc.errors():
        field_name = error["loc"][-1] if error["loc"] else "unknown"
        field_errors[field_name] = error["msg"]

    first_error = exc.errors()[0] if exc.errors() else {}
    field_name = first_error.get("loc", ["unknown"])[-1]
    message = first_error.get("msg", "Validation error")

    return JSONResponse(
        status_code=422,
        content={
            "type": "validation_error",
            "message": f"{field_name}: {message}",
            "data": {"fields": field_errors},
        },
    )


@app.get("/")
async def root():
    return {"message": "Oculog API is running!", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
