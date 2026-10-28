"""Product service — business rules around products."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.product import Product
from app.repositories.product_repo import ProductRepository
from app.schemas.product import PaginatedProducts, ProductCreate, ProductUpdate

settings = get_settings()


class ProductService:
    """Applies business rules and delegates persistence to the repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = ProductRepository(session)

    async def list_products(
        self, page: int = 1, page_size: int | None = None, category: str | None = None
    ) -> PaginatedProducts:
        """Return a paginated product list.

        Business rules:
        - page must be >= 1
        - page_size is bounded to [1, max_page_size]
        - page_size defaults to settings.default_page_size
        """
        if page < 1:
            raise ValueError("page must be >= 1")

        effective_size = page_size if page_size is not None else settings.default_page_size
        if effective_size < 1:
            raise ValueError("page_size must be >= 1")
        if effective_size > settings.max_page_size:
            raise ValueError(f"page_size must not exceed {settings.max_page_size}")

        return await self._repo.list_products(
            page=page, page_size=effective_size, category=category
        )

    async def get_product(self, product_id: int) -> Product:
        """Return a product by ID.  Raises LookupError if not found."""
        product = await self._repo.get_by_id(product_id)
        if product is None:
            raise LookupError(f"Product with id={product_id} not found")
        return product

    async def create_product(self, data: ProductCreate) -> Product:
        """Create a product.  Raises ValueError if name is duplicate."""
        existing = await self._repo.get_by_name(data.name)
        if existing is not None:
            raise ValueError(f"A product named '{data.name}' already exists")
        return await self._repo.create(data)

    async def update_product(self, product_id: int, data: ProductUpdate) -> Product:
        """Apply partial update.  Raises LookupError if product not found."""
        product = await self.get_product(product_id)
        if data.name is not None:
            # Ensure the new name is not taken by another product
            existing = await self._repo.get_by_name(data.name)
            if existing is not None and existing.id != product_id:
                raise ValueError(f"A product named '{data.name}' already exists")
        return await self._repo.update(product, data)

    async def delete_product(self, product_id: int) -> None:
        """Delete a product.  Raises LookupError if product not found."""
        product = await self.get_product(product_id)
        await self._repo.delete(product)
