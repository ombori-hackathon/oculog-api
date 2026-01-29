import uuid

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db import Base


class ConditionLog(Base):
    __tablename__ = "condition_logs"
    __table_args__ = (
        UniqueConstraint('user_id', 'log_date', name='uq_condition_logs_user_date'),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Date
    log_date: Mapped[Date] = mapped_column(Date, nullable=False)

    # Location
    city: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Rating & Symptoms (0-10)
    overall_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    burning: Mapped[int | None] = mapped_column(Integer, nullable=True)
    redness: Mapped[int | None] = mapped_column(Integer, nullable=True)
    itching: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tearing: Mapped[int | None] = mapped_column(Integer, nullable=True)
    swelling: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dryness: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Lifestyle Factors
    screen_time_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    sleep_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    sleep_quality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    water_intake_liters: Mapped[float | None] = mapped_column(Float, nullable=True)
    caffeine_cups: Mapped[int | None] = mapped_column(Integer, nullable=True)
    alcohol_units: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stress_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    outdoor_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Treatments Used (boolean)
    used_artificial_tears: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    used_warm_compress: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    used_lid_scrub: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    used_prescription_drops: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    used_omega3: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    used_humidifier: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Environment
    wore_contacts: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ac_exposure: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    heating_exposure: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Notes
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    treatments_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="condition_logs")
    weather_data = relationship(
        "WeatherData", back_populates="condition_log", uselist=False
    )
