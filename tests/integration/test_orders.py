"""Integration tests for order endpoints.

Test IDs: API-ORD-001 through API-ORD-012
"""


class TestOrders:
    """API-ORD-001 to API-ORD-012: GET /api/v1/orders, POST /api/v1/orders."""

    async def test_list_orders_empty_for_new_user(self, client, auth_headers):
        """API-ORD-001: A new user has no orders."""
        response = await client.get("/api/v1/orders", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_place_order_returns_201(self, client, auth_headers, sample_product):
        """API-ORD-002: Placing a valid order returns HTTP 201."""
        response = await client.post(
            "/api/v1/orders",
            json={"product_id": sample_product["id"], "quantity": 2},
            headers=auth_headers,
        )
        assert response.status_code == 201

    async def test_place_order_response_schema(self, client, auth_headers, sample_product):
        """API-ORD-003: Order response contains expected fields."""
        response = await client.post(
            "/api/v1/orders",
            json={"product_id": sample_product["id"], "quantity": 1},
            headers=auth_headers,
        )
        data = response.json()
        for field in ("id", "user_id", "product_id", "quantity", "unit_price", "status"):
            assert field in data

    async def test_order_appears_in_list(self, client, auth_headers, sample_product):
        """API-ORD-004: A placed order appears in the user's order list."""
        await client.post(
            "/api/v1/orders",
            json={"product_id": sample_product["id"], "quantity": 1},
            headers=auth_headers,
        )
        response = await client.get("/api/v1/orders", headers=auth_headers)
        assert response.json()["total"] == 1

    async def test_order_for_nonexistent_product_returns_404(self, client, auth_headers):
        """API-ORD-005: Ordering a non-existent product returns HTTP 404."""
        response = await client.post(
            "/api/v1/orders",
            json={"product_id": 99999, "quantity": 1},
            headers=auth_headers,
        )
        assert response.status_code == 404

    async def test_order_quantity_exceeds_stock_returns_422(self, client, auth_headers, sample_product):  # noqa: E501
        """API-ORD-006: Ordering more than available stock returns HTTP 422."""
        response = await client.post(
            "/api/v1/orders",
            json={"product_id": sample_product["id"], "quantity": 99999},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_order_unit_price_matches_product_price(self, client, auth_headers, sample_product):  # noqa: E501
        """API-ORD-007: Order unit_price equals the product price at time of order."""
        response = await client.post(
            "/api/v1/orders",
            json={"product_id": sample_product["id"], "quantity": 1},
            headers=auth_headers,
        )
        assert response.json()["unit_price"] == sample_product["price"]

    async def test_order_status_is_pending(self, client, auth_headers, sample_product):
        """API-ORD-008: Newly placed order has status='pending'."""
        response = await client.post(
            "/api/v1/orders",
            json={"product_id": sample_product["id"], "quantity": 1},
            headers=auth_headers,
        )
        assert response.json()["status"] == "pending"

    async def test_order_without_token_returns_401(self, client, sample_product):
        """API-ORD-009: Placing an order without authentication returns 401."""
        response = await client.post(
            "/api/v1/orders",
            json={"product_id": sample_product["id"], "quantity": 1},
        )
        assert response.status_code == 401

    async def test_order_with_zero_quantity_returns_422(self, client, auth_headers, sample_product):
        """API-ORD-010: Ordering zero quantity returns HTTP 422."""
        response = await client.post(
            "/api/v1/orders",
            json={"product_id": sample_product["id"], "quantity": 0},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_user_cannot_see_other_users_orders(self, client, auth_headers, sample_product):
        """API-ORD-011: A second user cannot see the first user's orders."""
        # Place an order as testuser
        await client.post(
            "/api/v1/orders",
            json={"product_id": sample_product["id"], "quantity": 1},
            headers=auth_headers,
        )
        # Register and login as a different user
        await client.post(
            "/api/v1/auth/register",
            json={"username": "otheruser", "email": "other@example.com", "password": "pass123456"},
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "otheruser", "password": "pass123456"},
        )
        other_token = login_resp.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        response = await client.get("/api/v1/orders", headers=other_headers)
        assert response.json()["total"] == 0  # other user sees only their own orders

    async def test_order_missing_product_id_returns_422(self, client, auth_headers):
        """API-ORD-012: Missing product_id in order body returns HTTP 422."""
        response = await client.post(
            "/api/v1/orders",
            json={"quantity": 1},
            headers=auth_headers,
        )
        assert response.status_code == 422
