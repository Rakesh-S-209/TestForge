"""Order repository — all database operations for orders."""

import math

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.schemas.order import OrderResponse, PaginatedOrders


class OrderRepository:
    """Encapsulates all order-related database access."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_user(
        self, user_id: int, page: int = 1, page_size: int = 20
    ) -> PaginatedOrders:
        count_result = await self._session.execute(
            select(func.count()).select_from(Order).where(Order.user_id == user_id)
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size
        result = await self._session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.id)
            .offset(offset)
            .limit(page_size)
        )
        items = list(result.scalars().all())
        pages = math.ceil(total / page_size) if page_size > 0 else 0

        return PaginatedOrders(
            items=[OrderResponse.model_validate(o) for o in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def create(  # noqa: PLR0913
        self, user_id: int, product_id: int, quantity: int, unit_price: float
    ) -> Order:
        order = Order(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            status="pending",
        )
        self._session.add(order)
        await self._session.commit()
        await self._session.refresh(order)
        return order
