"""Pydantic schemas for Product endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    """Shared product fields with validation."""

    name: str = Field(..., min_length=1, max_length=200, description="Product name (non-empty)")
    description: str = Field("", max_length=1000, description="Product description")
    price: float = Field(..., gt=0, description="Price must be greater than zero")
    stock: int = Field(0, ge=0, description="Stock quantity (non-negative integer)")
    category: str = Field("general", min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        """Reject names that are whitespace-only."""
        if not v.strip():
            raise ValueError("Product name must not be blank or whitespace-only")
        return v.strip()

    @field_validator("category")
    @classmethod
    def category_must_not_be_blank(cls, v: str) -> str:
        """Reject blank categories."""
        if not v.strip():
            raise ValueError("Category must not be blank")
        return v.strip().lower()


class ProductCreate(ProductBase):
    """Schema for creating a new product."""


class ProductUpdate(BaseModel):
    """Schema for updating an existing product.  All fields optional."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    category: str | None = Field(None, min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Product name must not be blank")
        return v.strip() if v else v

    @field_validator("category")
    @classmethod
    def category_must_not_be_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Category must not be blank")
        return v.strip().lower() if v else v


class ProductResponse(ProductBase):
    """Schema for returning a product from the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class PaginatedProducts(BaseModel):
    """Paginated list of products."""

    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    pages: int
