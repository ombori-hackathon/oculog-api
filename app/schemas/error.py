from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Unified error response format"""

    type: str
    message: str
    data: dict[str, Any] | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "duplicate_date",
                "message": "A log for this date already exists",
                "data": {"existing_log_id": "123e4567-e89b-12d3-a456-426614174000"},
            }
        }
    }
