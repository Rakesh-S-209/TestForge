"""Pydantic schemas for Order endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrderResponse(BaseModel):
    """Order as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    product_id: int
    quantity: int
    unit_price: float
    status: str
    created_at: datetime


class PaginatedOrders(BaseModel):
    """Paginated list of orders."""

    items: list[OrderResponse]
    total: int
    page: int
    page_size: int
    pages: int


class OrderCreate(BaseModel):
    """Schema for creating an order."""

    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1)
