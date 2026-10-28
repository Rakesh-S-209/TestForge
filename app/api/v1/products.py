"""Products router — CRUD endpoints for /api/v1/products."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import get_settings
from app.database import get_session
from app.models.user import User
from app.schemas.product import PaginatedProducts, ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])
settings = get_settings()


@router.get("", response_model=PaginatedProducts, summary="List all products")
async def list_products(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Items per page",
    ),
    category: str | None = Query(None, description="Filter by category"),
    session: AsyncSession = Depends(get_session),
) -> PaginatedProducts:
    """Return a paginated list of products."""
    svc = ProductService(session)
    try:
        return await svc.list_products(page=page, page_size=page_size, category=category)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.get("/{product_id}", response_model=ProductResponse, summary="Get a product by ID")
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
) -> ProductResponse:
    """Return a single product.  Returns 404 if the product does not exist."""
    svc = ProductService(session)
    try:
        product = await svc.get_product(product_id)
        return ProductResponse.model_validate(product)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product",
)
async def create_product(
    data: ProductCreate,
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> ProductResponse:
    """Create a new product.  Requires authentication.  Returns 409 on duplicate name."""
    svc = ProductService(session)
    try:
        product = await svc.create_product(data)
        return ProductResponse.model_validate(product)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.put("/{product_id}", response_model=ProductResponse, summary="Update a product")
async def update_product(
    product_id: int,
    data: ProductUpdate,
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> ProductResponse:
    """Update an existing product.  Requires authentication."""
    svc = ProductService(session)
    try:
        product = await svc.update_product(product_id, data)
        return ProductResponse.model_validate(product)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
)
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(get_current_user),
) -> None:
    """Delete a product.  Requires authentication.  Returns 204 on success."""
    svc = ProductService(session)
    try:
        await svc.delete_product(product_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
