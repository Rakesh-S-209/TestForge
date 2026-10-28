"""Orders router — /api/v1/orders endpoints (authenticated)."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import get_settings
from app.database import get_session
from app.models.user import User
from app.repositories.order_repo import OrderRepository
from app.repositories.product_repo import ProductRepository
from app.schemas.order import OrderCreate, OrderResponse, PaginatedOrders

router = APIRouter(prefix="/orders", tags=["orders"])
settings = get_settings()


@router.get("", response_model=PaginatedOrders, summary="List orders for authenticated user")
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedOrders:
    """Return paginated orders belonging to the authenticated user."""
    repo = OrderRepository(session)
    return await repo.list_for_user(user_id=current_user.id, page=page, page_size=page_size)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Place an order",
)
async def create_order(
    data: OrderCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> OrderResponse:
    """Place an order for a product.  Product must exist and have sufficient stock."""
    product_repo = ProductRepository(session)
    product = await product_repo.get_by_id(data.product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {data.product_id} not found",
        )
    if product.stock < data.quantity:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Insufficient stock: available={product.stock}, requested={data.quantity}",
        )

    order_repo = OrderRepository(session)
    order = await order_repo.create(
        user_id=current_user.id,
        product_id=data.product_id,
        quantity=data.quantity,
        unit_price=product.price,
    )
    return OrderResponse.model_validate(order)
