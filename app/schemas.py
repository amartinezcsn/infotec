from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


Category = Literal["pasteles-personalizados", "cupcakes", "galletas-decoradas"]


class ProductImport(BaseModel):
    source_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    category: Category
    description: str = ""
    base_price: Decimal = Field(ge=0)
    currency: Literal["MXN"] = "MXN"
    variants: list[dict[str, Any]] = []
    image_url: HttpUrl | None = None
    product_url: HttpUrl
    published: bool = True
    source_updated_at: datetime


class OrderRequestCreate(BaseModel):
    idempotency_key: str = Field(min_length=8)
    customer_name: str = Field(min_length=1, max_length=100)
    product_id: str
    quantity_or_portions: str = Field(min_length=1)
    flavor: str = Field(min_length=1)
    filling: str | None = None
    theme: str = Field(min_length=1)
    colors: list[str] = []
    inscription: str | None = None
    dietary_notes: list[str] = []
    budget_amount: Decimal | None = Field(default=None, ge=0)
    requested_at: datetime
    fulfillment_mode: Literal["delivery", "pickup"]
    delivery_zone_or_postal_code: str | None = None
    customer_notes: str | None = None
    customer_confirmed_summary: bool

    @field_validator("customer_confirmed_summary")
    @classmethod
    def summary_must_be_confirmed(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("El cliente debe confirmar el resumen")
        return value


class CapacityCheck(BaseModel):
    requested_at: datetime
    requested_minutes: int = Field(gt=0, le=1440)


class AvailabilityReview(BaseModel):
    decision: Literal["availability_approved", "alternative_proposed", "availability_rejected"]
    reviewer_id: str = Field(min_length=1)
    comment: str | None = None
    alternative_at: datetime | None = None


class QuoteCreate(BaseModel):
    base_amount: Decimal = Field(ge=0)
    adjustments: list[dict[str, Any]] = []
    total: Decimal = Field(ge=0)
    valid_until: datetime | None = None


class ChatMessage(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CalendarBlock(BaseModel):
    slot_date: str
    capacity_minutes: int = Field(ge=0, le=1440)
    reserved_minutes: int = Field(ge=0, le=1440)
    blocked: bool = False
    notes: str | None = None

