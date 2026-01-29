from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.dependencies import get_current_user
from app.exceptions import AppException, ErrorType
from app.models.condition_log import ConditionLog
from app.models.user import User
from app.models.weather_data import WeatherData
from app.schemas.condition_log import (
    ConditionLogCreate,
    ConditionLogDetailResponse,
    ConditionLogResponse,
    ConditionLogUpdate,
    PaginatedLogsResponse,
    SortField,
    SortOrder,
)
from app.schemas.weather import UnifiedWeatherResponse

router = APIRouter(prefix="/logs", tags=["condition_logs"])


def weather_data_to_unified(weather: WeatherData | None) -> UnifiedWeatherResponse | None:
    """Convert WeatherData model to UnifiedWeatherResponse."""
    if weather is None:
        return None
    return UnifiedWeatherResponse(
        location_name=weather.location_name,
        latitude=weather.latitude,
        longitude=weather.longitude,
        temperature_c=weather.temperature_c,
        condition=weather.conditions,
        icon_code=None,  # Not stored in WeatherData
        humidity_percent=weather.humidity_percent,
        pressure_hpa=weather.pressure_hpa,
        wind_speed_kmh=weather.wind_speed_kmh,
        air_quality_index=weather.air_quality_index,
        uv_index=weather.uv_index,
        pollen_count=weather.pollen_count,
        recorded_at=weather.recorded_at,
    )


@router.get("", response_model=PaginatedLogsResponse)
def get_logs(
    start_date: date | None = Query(None, description="Filter logs from this date"),
    end_date: date | None = Query(None, description="Filter logs until this date"),
    sort_by: SortField = Query(SortField.date, description="Field to sort by"),
    order: SortOrder = Query(SortOrder.desc, description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all condition logs for the current user with pagination and optional date filters"""
    query = db.query(ConditionLog).filter(ConditionLog.user_id == current_user.id)

    if start_date:
        query = query.filter(ConditionLog.log_date >= start_date)
    if end_date:
        query = query.filter(ConditionLog.log_date <= end_date)

    # Build ORDER BY clause based on sort parameters
    if sort_by == SortField.date:
        sort_column = ConditionLog.log_date
        use_nulls_last = False
    elif sort_by == SortField.rating:
        sort_column = ConditionLog.overall_rating
        use_nulls_last = True
    else:  # city
        sort_column = ConditionLog.city
        use_nulls_last = True

    if order == SortOrder.asc:
        order_clause = sort_column.asc().nulls_last() if use_nulls_last else sort_column.asc()
    else:  # desc
        order_clause = sort_column.desc().nulls_last() if use_nulls_last else sort_column.desc()

    total = query.count()
    items = (
        query.order_by(order_clause)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedLogsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total > 0 else 1,
    )


@router.get("/{log_id}", response_model=ConditionLogDetailResponse)
def get_log(
    log_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific condition log by ID with weather data"""
    log = (
        db.query(ConditionLog)
        .options(joinedload(ConditionLog.weather_data))
        .filter(ConditionLog.id == log_id)
        .first()
    )
    if log is None:
        raise AppException(
            status_code=404,
            error_type=ErrorType.NOT_FOUND,
            message="Condition log not found",
            data={"resource": "condition_log", "id": str(log_id)},
        )
    if log.user_id != current_user.id:
        raise AppException(
            status_code=403,
            error_type=ErrorType.FORBIDDEN,
            message="Not authorized",
        )

    return ConditionLogDetailResponse(
        id=log.id,
        user_id=log.user_id,
        log_date=log.log_date,
        overall_rating=log.overall_rating,
        burning=log.burning,
        redness=log.redness,
        itching=log.itching,
        tearing=log.tearing,
        swelling=log.swelling,
        screen_time_hours=log.screen_time_hours,
        sleep_hours=log.sleep_hours,
        sleep_quality=log.sleep_quality,
        water_intake_liters=log.water_intake_liters,
        caffeine_cups=log.caffeine_cups,
        alcohol_units=log.alcohol_units,
        stress_level=log.stress_level,
        outdoor_hours=log.outdoor_hours,
        used_artificial_tears=log.used_artificial_tears,
        used_warm_compress=log.used_warm_compress,
        used_lid_scrub=log.used_lid_scrub,
        used_prescription_drops=log.used_prescription_drops,
        used_omega3=log.used_omega3,
        used_humidifier=log.used_humidifier,
        wore_contacts=log.wore_contacts,
        ac_exposure=log.ac_exposure,
        heating_exposure=log.heating_exposure,
        comments=log.comments,
        treatments_notes=log.treatments_notes,
        created_at=log.created_at,
        updated_at=log.updated_at,
        weather=weather_data_to_unified(log.weather_data),
    )


@router.post("", response_model=ConditionLogResponse, status_code=201)
def create_log(
    log: ConditionLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new condition log"""
    log_data = log.model_dump(exclude={"user_id"})
    db_log = ConditionLog(**log_data, user_id=current_user.id)
    db.add(db_log)
    try:
        db.commit()
        db.refresh(db_log)
        return db_log
    except IntegrityError as e:
        db.rollback()
        # PostgreSQL error code 23505 = unique_violation
        pg_code = getattr(e.orig, "pgcode", None)
        if pg_code == "23505":
            existing = (
                db.query(ConditionLog)
                .filter(
                    ConditionLog.user_id == current_user.id,
                    ConditionLog.log_date == log.log_date,
                )
                .first()
            )
            raise AppException(
                status_code=409,
                error_type=ErrorType.DUPLICATE_DATE,
                message="A log for this date already exists",
                data={"existing_log_id": str(existing.id) if existing else None},
            )
        raise AppException(
            status_code=500,
            error_type=ErrorType.SERVER_ERROR,
            message="Database error occurred",
        )


@router.put("/{log_id}", response_model=ConditionLogResponse)
def update_log(
    log_id: UUID,
    log_update: ConditionLogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a condition log"""
    db_log = db.query(ConditionLog).filter(ConditionLog.id == log_id).first()
    if db_log is None:
        raise AppException(
            status_code=404,
            error_type=ErrorType.NOT_FOUND,
            message="Condition log not found",
            data={"resource": "condition_log", "id": str(log_id)},
        )
    if db_log.user_id != current_user.id:
        raise AppException(
            status_code=403,
            error_type=ErrorType.FORBIDDEN,
            message="Not authorized",
        )

    update_data = log_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_log, field, value)

    try:
        db.commit()
        db.refresh(db_log)
        return db_log
    except IntegrityError as e:
        db.rollback()
        # PostgreSQL error code 23505 = unique_violation
        pg_code = getattr(e.orig, "pgcode", None)
        if pg_code == "23505":
            existing = (
                db.query(ConditionLog)
                .filter(
                    ConditionLog.user_id == current_user.id,
                    ConditionLog.log_date == log_update.log_date,
                    ConditionLog.id != log_id,
                )
                .first()
            )
            raise AppException(
                status_code=409,
                error_type=ErrorType.DUPLICATE_DATE,
                message="A log for this date already exists",
                data={"existing_log_id": str(existing.id) if existing else None},
            )
        raise AppException(
            status_code=500,
            error_type=ErrorType.SERVER_ERROR,
            message="Database error occurred",
        )


@router.delete("/{log_id}", status_code=204)
def delete_log(
    log_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a condition log"""
    db_log = db.query(ConditionLog).filter(ConditionLog.id == log_id).first()
    if db_log is None:
        raise AppException(
            status_code=404,
            error_type=ErrorType.NOT_FOUND,
            message="Condition log not found",
            data={"resource": "condition_log", "id": str(log_id)},
        )
    if db_log.user_id != current_user.id:
        raise AppException(
            status_code=403,
            error_type=ErrorType.FORBIDDEN,
            message="Not authorized",
        )

    db.delete(db_log)
    db.commit()
    return None
