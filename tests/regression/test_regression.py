"""Regression tests for confirmed and fixed defects.

Each test is tied to a defect in the defect log (docs/defect_log.md).

DEFECT-001: Price validation — zero price was previously accepted.
DEFECT-002: Pagination — page_size=0 caused a ZeroDivisionError.
DEFECT-003: Authorization — unauthenticated users could create products.
"""



class TestDefect001PriceValidation:
    """Regression for DEFECT-001: price=0 must be rejected."""

    async def test_zero_price_rejected_via_api(self, client, auth_headers):
        """REGRESSION-001: POST /products with price=0 must return 422 (not 201).

        Previously the API accepted price=0, violating the business rule that
        prices must be > 0.  This regression test ensures the fix holds.
        """
        response = await client.post(
            "/api/v1/products",
            json={"name": "Free Widget", "price": 0, "stock": 1, "category": "misc"},
            headers=auth_headers,
        )
        assert response.status_code == 422, (
            "REGRESSION-001 FAILED: price=0 was accepted, defect re-introduced"
        )

    async def test_negative_price_rejected_via_api(self, client, auth_headers):
        """REGRESSION-001b: POST /products with price=-1.0 must return 422."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "Debt Widget", "price": -1.0, "stock": 1, "category": "misc"},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestDefect002PaginationBoundary:
    """Regression for DEFECT-002: page_size=0 must not cause server error."""

    async def test_page_size_zero_returns_422_not_500(self, client):
        """REGRESSION-002: page_size=0 must return 422, never 500.

        Previously page_size=0 reached the service and caused ZeroDivisionError
        when calculating page count.  FastAPI query validation now catches this.
        """
        response = await client.get("/api/v1/products?page_size=0")
        assert response.status_code == 422, (
            "REGRESSION-002 FAILED: page_size=0 caused a server error, defect re-introduced"
        )
        assert response.status_code != 500

    async def test_page_zero_returns_422_not_500(self, client):
        """REGRESSION-002b: page=0 must return 422, never 500."""
        response = await client.get("/api/v1/products?page=0")
        assert response.status_code == 422
        assert response.status_code != 500


class TestDefect003Authorization:
    """Regression for DEFECT-003: unauthenticated product creation must be rejected."""

    async def test_create_product_without_auth_returns_401(self, client):
        """REGRESSION-003: POST /products without token must return 401.

        Previously there was no auth check on the create endpoint.
        Anyone could modify the product catalogue without credentials.
        This regression test ensures the endpoint remains protected.
        """
        response = await client.post(
            "/api/v1/products",
            json={"name": "Sneaky Widget", "price": 1.0, "stock": 1, "category": "misc"},
        )
        assert response.status_code == 401, (
            "REGRESSION-003 FAILED: product created without authentication, defect re-introduced"
        )

    async def test_update_product_without_auth_returns_401(self, client, sample_product):
        """REGRESSION-003b: PUT /products/{id} without token must return 401."""
        response = await client.put(
            f"/api/v1/products/{sample_product['id']}",
            json={"price": 5.0},
        )
        assert response.status_code == 401

    async def test_delete_product_without_auth_returns_401(self, client, sample_product):
        """REGRESSION-003c: DELETE /products/{id} without token must return 401."""
        response = await client.delete(f"/api/v1/products/{sample_product['id']}")
        assert response.status_code == 401
