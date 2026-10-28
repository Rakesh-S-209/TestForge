"""Unit tests for ProductCreate and ProductUpdate Pydantic schemas.

Test IDs: VAL-PROD-001 through VAL-PROD-020
These tests validate business rules enforced at the schema layer,
independently of the database and HTTP stack.
"""

import pytest
from pydantic import ValidationError

from app.schemas.product import ProductCreate, ProductUpdate


class TestProductCreateValidation:
    """VAL-PROD-001 to VAL-PROD-012: ProductCreate schema validation."""

    def test_valid_product(self):
        """VAL-PROD-001: A fully valid product passes validation."""
        p = ProductCreate(name="Widget", price=9.99, stock=10, category="tools")
        assert p.name == "Widget"
        assert p.price == 9.99
        assert p.stock == 10

    def test_name_stripped_of_whitespace(self):
        """VAL-PROD-002: Leading/trailing whitespace is stripped from name."""
        p = ProductCreate(name="  Gadget  ", price=1.0, stock=5, category="electronics")
        assert p.name == "Gadget"

    def test_empty_name_raises(self):
        """VAL-PROD-003: An empty name string must raise ValidationError."""
        with pytest.raises(ValidationError):
            ProductCreate(name="", price=9.99, stock=0, category="tools")

    def test_whitespace_only_name_raises(self):
        """VAL-PROD-004: A whitespace-only name must raise ValidationError."""
        with pytest.raises(ValidationError):
            ProductCreate(name="   ", price=9.99, stock=0, category="tools")

    def test_zero_price_raises(self):
        """VAL-PROD-005: Price of zero must raise ValidationError (price must be > 0)."""
        with pytest.raises(ValidationError):
            ProductCreate(name="Item", price=0, stock=5, category="tools")

    def test_negative_price_raises(self):
        """VAL-PROD-006: Negative price must raise ValidationError."""
        with pytest.raises(ValidationError):
            ProductCreate(name="Item", price=-1.0, stock=5, category="tools")

    def test_negative_stock_raises(self):
        """VAL-PROD-007: Negative stock must raise ValidationError."""
        with pytest.raises(ValidationError):
            ProductCreate(name="Item", price=5.0, stock=-1, category="tools")

    def test_zero_stock_is_valid(self):
        """VAL-PROD-008: Zero stock is a valid quantity (out of stock)."""
        p = ProductCreate(name="Rare Item", price=100.0, stock=0, category="rare")
        assert p.stock == 0

    def test_very_small_positive_price(self):
        """VAL-PROD-009: The smallest positive float is a valid price."""
        p = ProductCreate(name="Penny Item", price=0.01, stock=1, category="cheap")
        assert p.price == pytest.approx(0.01)

    def test_missing_name_raises(self):
        """VAL-PROD-010: Omitting name raises ValidationError."""
        with pytest.raises(ValidationError):
            ProductCreate(price=9.99, stock=0, category="tools")  # type: ignore[call-arg]

    def test_missing_price_raises(self):
        """VAL-PROD-011: Omitting price raises ValidationError."""
        with pytest.raises(ValidationError):
            ProductCreate(name="Item", stock=0, category="tools")  # type: ignore[call-arg]

    def test_category_normalised_to_lowercase(self):
        """VAL-PROD-012: Category is normalised to lowercase."""
        p = ProductCreate(name="Item", price=1.0, stock=0, category="ELECTRONICS")
        assert p.category == "electronics"

    def test_non_string_price_coerced_or_rejected(self):
        """VAL-PROD-013: A string that is not numeric for price raises ValidationError."""
        with pytest.raises(ValidationError):
            ProductCreate(name="Item", price="free", stock=0, category="tools")  # type: ignore[arg-type]


class TestProductUpdateValidation:
    """VAL-PROD-014 to VAL-PROD-020: ProductUpdate schema validation."""

    def test_empty_update_is_valid(self):
        """VAL-PROD-014: An update with no fields set is valid (no-op update)."""
        upd = ProductUpdate()
        assert upd.model_dump(exclude_unset=True) == {}

    def test_partial_update_with_price(self):
        """VAL-PROD-015: Updating only price is valid."""
        upd = ProductUpdate(price=49.99)
        assert upd.price == 49.99
        assert upd.name is None

    def test_zero_price_in_update_raises(self):
        """VAL-PROD-016: A zero price in an update raises ValidationError."""
        with pytest.raises(ValidationError):
            ProductUpdate(price=0.0)

    def test_negative_price_in_update_raises(self):
        """VAL-PROD-017: A negative price in an update raises ValidationError."""
        with pytest.raises(ValidationError):
            ProductUpdate(price=-5.0)

    def test_negative_stock_in_update_raises(self):
        """VAL-PROD-018: Negative stock in an update raises ValidationError."""
        with pytest.raises(ValidationError):
            ProductUpdate(stock=-1)

    def test_blank_name_in_update_raises(self):
        """VAL-PROD-019: A blank name string in an update raises ValidationError."""
        with pytest.raises(ValidationError):
            ProductUpdate(name="  ")

    def test_update_category_normalised(self):
        """VAL-PROD-020: Category in update is normalised to lowercase."""
        upd = ProductUpdate(category="GADGETS")
        assert upd.category == "gadgets"
