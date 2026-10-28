"""Product repository — all database operations for products.

Uses parameterised SQLAlchemy queries to prevent SQL injection.
"""

import math

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import PaginatedProducts, ProductCreate, ProductResponse, ProductUpdate


class ProductRepository:
    """Encapsulates all product-related database access."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, product_id: int) -> Product | None:
        """Return the product with the given ID, or None."""
        result = await self._session.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Product | None:
        """Return a product matching the exact name (case-insensitive), or None."""
        result = await self._session.execute(
            select(Product).where(func.lower(Product.name) == name.strip().lower())
        )
        return result.scalar_one_or_none()

    async def list_products(
        self, page: int = 1, page_size: int = 20, category: str | None = None
    ) -> PaginatedProducts:
        """Return a paginated list of products, optionally filtered by category."""
        query = select(Product)
        count_query = select(func.count()).select_from(Product)

        if category:
            query = query.where(func.lower(Product.category) == category.lower())
            count_query = count_query.where(func.lower(Product.category) == category.lower())

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        result = await self._session.execute(
            query.order_by(Product.id).offset(offset).limit(page_size)
        )
        items = list(result.scalars().all())
        pages = math.ceil(total / page_size) if page_size > 0 else 0

        return PaginatedProducts(
            items=[ProductResponse.model_validate(p) for p in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def create(self, data: ProductCreate) -> Product:
        """Insert a new product and return it."""
        product = Product(**data.model_dump())
        self._session.add(product)
        await self._session.commit()
        await self._session.refresh(product)
        return product

    async def update(self, product: Product, data: ProductUpdate) -> Product:
        """Apply partial updates to a product and persist them."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        await self._session.commit()
        await self._session.refresh(product)
        return product

    async def delete(self, product: Product) -> None:
        """Delete a product from the database."""
        await self._session.delete(product)
        await self._session.commit()
