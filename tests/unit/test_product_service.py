"""Unit tests for ProductService business logic.

Test IDs: SVC-PROD-001 through SVC-PROD-015
Tests use a real in-memory SQLite database (via session fixture) to
exercise the service layer including its business rules.
"""

import pytest

from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import ProductService


class TestProductServiceList:
    """SVC-PROD-001 to SVC-PROD-004: list_products pagination and filtering."""

    async def test_empty_list_returns_zero_total(self, session):
        """SVC-PROD-001: An empty database returns total=0."""
        svc = ProductService(session)
        result = await svc.list_products()
        assert result.total == 0
        assert result.items == []

    async def test_page_below_one_raises(self, session):
        """SVC-PROD-002: page < 1 raises ValueError."""
        svc = ProductService(session)
        with pytest.raises(ValueError, match="page must be"):
            await svc.list_products(page=0)

    async def test_page_size_above_max_raises(self, session):
        """SVC-PROD-003: page_size > max_page_size raises ValueError."""
        svc = ProductService(session)
        with pytest.raises(ValueError, match="page_size must not exceed"):
            await svc.list_products(page_size=9999)

    async def test_page_size_zero_raises(self, session):
        """SVC-PROD-004: page_size=0 raises ValueError."""
        svc = ProductService(session)
        with pytest.raises(ValueError, match="page_size must be"):
            await svc.list_products(page_size=0)


class TestProductServiceCRUD:
    """SVC-PROD-005 to SVC-PROD-012: create, get, update, delete."""

    async def test_create_product_returns_product_with_id(self, session):
        """SVC-PROD-005: A newly created product has an assigned integer ID."""
        svc = ProductService(session)
        data = ProductCreate(name="Test Widget", price=9.99, stock=50, category="tools")
        product = await svc.create_product(data)
        assert product.id is not None
        assert product.id > 0
        assert product.name == "Test Widget"

    async def test_get_product_returns_correct_product(self, session):
        """SVC-PROD-006: get_product returns the product with the matching ID."""
        svc = ProductService(session)
        data = ProductCreate(name="Findable Product", price=5.0, stock=10, category="misc")
        created = await svc.create_product(data)
        found = await svc.get_product(created.id)
        assert found.id == created.id
        assert found.name == "Findable Product"

    async def test_get_product_not_found_raises_lookup_error(self, session):
        """SVC-PROD-007: get_product raises LookupError for a non-existent ID."""
        svc = ProductService(session)
        with pytest.raises(LookupError):
            await svc.get_product(99999)

    async def test_duplicate_name_raises_value_error(self, session):
        """SVC-PROD-008: Creating two products with the same name raises ValueError."""
        svc = ProductService(session)
        data = ProductCreate(name="Unique Widget", price=1.0, stock=5, category="tools")
        await svc.create_product(data)
        with pytest.raises(ValueError, match="already exists"):
            await svc.create_product(data)

    async def test_update_product_price(self, session):
        """SVC-PROD-009: update_product applies the new price correctly."""
        svc = ProductService(session)
        product = await svc.create_product(
            ProductCreate(name="Old Price", price=10.0, stock=5, category="misc")
        )
        updated = await svc.update_product(product.id, ProductUpdate(price=19.99))
        assert updated.price == pytest.approx(19.99)
        assert updated.name == "Old Price"  # unchanged field

    async def test_update_nonexistent_product_raises_lookup_error(self, session):
        """SVC-PROD-010: Updating a non-existent product raises LookupError."""
        svc = ProductService(session)
        with pytest.raises(LookupError):
            await svc.update_product(99999, ProductUpdate(price=5.0))

    async def test_delete_product_removes_it(self, session):
        """SVC-PROD-011: After deletion, get_product raises LookupError."""
        svc = ProductService(session)
        product = await svc.create_product(
            ProductCreate(name="Deletable", price=1.0, stock=0, category="misc")
        )
        await svc.delete_product(product.id)
        with pytest.raises(LookupError):
            await svc.get_product(product.id)

    async def test_delete_nonexistent_raises_lookup_error(self, session):
        """SVC-PROD-012: Deleting a non-existent product raises LookupError."""
        svc = ProductService(session)
        with pytest.raises(LookupError):
            await svc.delete_product(99999)

    async def test_list_returns_all_created_products(self, session):
        """SVC-PROD-013: Products created are all visible in list."""
        svc = ProductService(session)
        for i in range(5):
            await svc.create_product(
                ProductCreate(name=f"Product {i}", price=float(i + 1), stock=i, category="misc")
            )
        result = await svc.list_products(page=1, page_size=10)
        assert result.total == 5
        assert len(result.items) == 5

    async def test_pagination_page_2(self, session):
        """SVC-PROD-014: Page 2 of 3-item list with page_size=2 returns 1 item."""
        svc = ProductService(session)
        for i in range(3):
            await svc.create_product(
                ProductCreate(name=f"Paged {i}", price=1.0, stock=0, category="misc")
            )
        result = await svc.list_products(page=2, page_size=2)
        assert len(result.items) == 1
        assert result.total == 3
        assert result.pages == 2

    async def test_category_filter(self, session):
        """SVC-PROD-015: Category filter returns only matching products."""
        svc = ProductService(session)
        await svc.create_product(
            ProductCreate(name="Tool A", price=1.0, stock=1, category="tools")
        )
        await svc.create_product(
            ProductCreate(name="Gadget B", price=2.0, stock=1, category="gadgets")
        )
        result = await svc.list_products(category="tools")
        assert result.total == 1
        assert result.items[0].name == "Tool A"
