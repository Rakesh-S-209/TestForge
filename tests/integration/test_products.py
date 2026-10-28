"""Integration tests for product endpoints.

Test IDs: API-PROD-001 through API-PROD-040
Covers: list, get, create, update, delete, pagination, filtering,
        negative cases, boundary cases, and schema validation.
"""

import pytest


class TestListProducts:
    """API-PROD-001 to API-PROD-006: GET /api/v1/products."""

    async def test_list_products_empty_returns_200(self, client):
        """API-PROD-001: Empty store returns 200 with empty items list."""
        response = await client.get("/api/v1/products")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_list_products_response_schema(self, client):
        """API-PROD-002: Response includes pagination metadata fields."""
        response = await client.get("/api/v1/products")
        data = response.json()
        for field in ("items", "total", "page", "page_size", "pages"):
            assert field in data, f"Missing field: {field}"

    async def test_list_products_includes_created_product(self, client, sample_product):
        """API-PROD-003: A created product appears in the list."""
        response = await client.get("/api/v1/products")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == sample_product["id"]

    async def test_list_products_pagination_page_2(self, client, auth_headers):
        """API-PROD-004: Page 2 of a 3-item list with page_size=2 returns 1 item."""
        for i in range(3):
            await client.post(
                "/api/v1/products",
                json={"name": f"P{i}", "price": float(i + 1), "stock": 0, "category": "misc"},
                headers=auth_headers,
            )
        response = await client.get("/api/v1/products?page=2&page_size=2")
        data = response.json()
        assert len(data["items"]) == 1
        assert data["pages"] == 2

    async def test_list_products_category_filter(self, client, auth_headers):
        """API-PROD-005: Category filter returns only matching products."""
        await client.post(
            "/api/v1/products",
            json={"name": "Hammer", "price": 15.0, "stock": 5, "category": "tools"},
            headers=auth_headers,
        )
        await client.post(
            "/api/v1/products",
            json={"name": "Laptop", "price": 999.0, "stock": 3, "category": "electronics"},
            headers=auth_headers,
        )
        response = await client.get("/api/v1/products?category=tools")
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Hammer"

    async def test_list_products_page_size_too_large_returns_422(self, client):
        """API-PROD-006: page_size > 100 returns HTTP 422."""
        response = await client.get("/api/v1/products?page_size=9999")
        assert response.status_code == 422


class TestGetProduct:
    """API-PROD-007 to API-PROD-010: GET /api/v1/products/{id}."""

    async def test_get_existing_product_returns_200(self, client, sample_product):
        """API-PROD-007: GET for an existing product returns HTTP 200."""
        response = await client.get(f"/api/v1/products/{sample_product['id']}")
        assert response.status_code == 200

    async def test_get_product_response_matches_created(self, client, sample_product):
        """API-PROD-008: GET response matches the data used at creation."""
        response = await client.get(f"/api/v1/products/{sample_product['id']}")
        data = response.json()
        assert data["name"] == sample_product["name"]
        assert data["price"] == sample_product["price"]
        assert data["stock"] == sample_product["stock"]

    async def test_get_nonexistent_product_returns_404(self, client):
        """API-PROD-009: GET for a non-existent product returns HTTP 404."""
        response = await client.get("/api/v1/products/99999")
        assert response.status_code == 404

    async def test_get_product_response_has_timestamps(self, client, sample_product):
        """API-PROD-010: Response includes created_at and updated_at timestamps."""
        response = await client.get(f"/api/v1/products/{sample_product['id']}")
        data = response.json()
        assert "created_at" in data
        assert "updated_at" in data


class TestCreateProduct:
    """API-PROD-011 to API-PROD-020: POST /api/v1/products."""

    async def test_create_product_returns_201(self, client, auth_headers):
        """API-PROD-011: A valid product creation returns HTTP 201."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "New Widget", "price": 29.99, "stock": 50, "category": "widgets"},
            headers=auth_headers,
        )
        assert response.status_code == 201

    async def test_create_product_response_schema(self, client, auth_headers):
        """API-PROD-012: Response contains all expected product fields."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "Schema Widget", "price": 9.99, "stock": 5, "category": "misc"},
            headers=auth_headers,
        )
        data = response.json()
        for field in ("id", "name", "price", "stock", "category", "created_at", "updated_at"):
            assert field in data, f"Missing field: {field}"

    async def test_create_product_with_zero_price_returns_422(self, client, auth_headers):
        """API-PROD-013: Zero price returns HTTP 422."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "Free Widget", "price": 0, "stock": 1, "category": "misc"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_create_product_with_negative_price_returns_422(self, client, auth_headers):
        """API-PROD-014: Negative price returns HTTP 422."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "Negative Widget", "price": -5.0, "stock": 1, "category": "misc"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_create_product_empty_name_returns_422(self, client, auth_headers):
        """API-PROD-015: Empty name returns HTTP 422."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "", "price": 9.99, "stock": 1, "category": "misc"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_create_product_negative_stock_returns_422(self, client, auth_headers):
        """API-PROD-016: Negative stock returns HTTP 422."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "Widget", "price": 9.99, "stock": -1, "category": "misc"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_create_duplicate_name_returns_409(self, client, auth_headers, sample_product):
        """API-PROD-017: Duplicate product name returns HTTP 409."""
        response = await client.post(
            "/api/v1/products",
            json={"name": sample_product["name"], "price": 1.0, "stock": 0, "category": "misc"},
            headers=auth_headers,
        )
        assert response.status_code == 409

    async def test_create_product_missing_required_fields_returns_422(self, client, auth_headers):
        """API-PROD-018: Missing required fields return HTTP 422."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "Incomplete"},  # missing price
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_create_product_wrong_type_for_price_returns_422(self, client, auth_headers):
        """API-PROD-019: A string 'price' field returns HTTP 422."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "Widget", "price": "cheap", "stock": 1, "category": "misc"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_create_product_zero_stock_is_valid(self, client, auth_headers):
        """API-PROD-020: Zero stock is valid (out-of-stock product)."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "Rare Item", "price": 999.99, "stock": 0, "category": "rare"},
            headers=auth_headers,
        )
        assert response.status_code == 201


class TestUpdateProduct:
    """API-PROD-021 to API-PROD-028: PUT /api/v1/products/{id}."""

    async def test_update_price_returns_200(self, client, auth_headers, sample_product):
        """API-PROD-021: Updating price returns HTTP 200."""
        response = await client.put(
            f"/api/v1/products/{sample_product['id']}",
            json={"price": 49.99},
            headers=auth_headers,
        )
        assert response.status_code == 200

    async def test_update_price_reflects_in_response(self, client, auth_headers, sample_product):
        """API-PROD-022: Updated price is reflected in the response body."""
        await client.put(
            f"/api/v1/products/{sample_product['id']}",
            json={"price": 49.99},
            headers=auth_headers,
        )
        response = await client.get(f"/api/v1/products/{sample_product['id']}")
        assert response.json()["price"] == pytest.approx(49.99)

    async def test_update_nonexistent_product_returns_404(self, client, auth_headers):
        """API-PROD-023: Update of non-existent product returns HTTP 404."""
        response = await client.put(
            "/api/v1/products/99999",
            json={"price": 5.0},
            headers=auth_headers,
        )
        assert response.status_code == 404

    async def test_update_to_zero_price_returns_422(self, client, auth_headers, sample_product):
        """API-PROD-024: Updating price to 0 returns HTTP 422."""
        response = await client.put(
            f"/api/v1/products/{sample_product['id']}",
            json={"price": 0},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_update_stock_to_valid_value(self, client, auth_headers, sample_product):
        """API-PROD-025: Updating stock to a valid value succeeds."""
        response = await client.put(
            f"/api/v1/products/{sample_product['id']}",
            json={"stock": 200},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["stock"] == 200

    async def test_update_name_to_existing_name_returns_409(self, client, auth_headers, sample_product):  # noqa: E501
        """API-PROD-026: Renaming a product to an already-taken name returns 409."""
        await client.post(
            "/api/v1/products",
            json={"name": "Second Product", "price": 5.0, "stock": 1, "category": "misc"},
            headers=auth_headers,
        )
        response = await client.put(
            f"/api/v1/products/{sample_product['id']}",
            json={"name": "Second Product"},
            headers=auth_headers,
        )
        assert response.status_code == 409

    async def test_update_partial_fields_only(self, client, auth_headers, sample_product):
        """API-PROD-027: Only specified fields change; others remain."""
        original_name = sample_product["name"]
        response = await client.put(
            f"/api/v1/products/{sample_product['id']}",
            json={"stock": 999},
            headers=auth_headers,
        )
        assert response.json()["name"] == original_name
        assert response.json()["stock"] == 999

    async def test_update_with_empty_body_returns_200(self, client, auth_headers, sample_product):
        """API-PROD-028: An empty update body is a valid no-op update."""
        response = await client.put(
            f"/api/v1/products/{sample_product['id']}",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 200


class TestDeleteProduct:
    """API-PROD-029 to API-PROD-033: DELETE /api/v1/products/{id}."""

    async def test_delete_existing_product_returns_204(self, client, auth_headers, sample_product):
        """API-PROD-029: Deleting an existing product returns HTTP 204."""
        response = await client.delete(
            f"/api/v1/products/{sample_product['id']}", headers=auth_headers
        )
        assert response.status_code == 204

    async def test_deleted_product_not_found_on_get(self, client, auth_headers, sample_product):
        """API-PROD-030: A deleted product returns 404 on subsequent GET."""
        await client.delete(f"/api/v1/products/{sample_product['id']}", headers=auth_headers)
        response = await client.get(f"/api/v1/products/{sample_product['id']}")
        assert response.status_code == 404

    async def test_delete_nonexistent_product_returns_404(self, client, auth_headers):
        """API-PROD-031: Deleting a non-existent product returns HTTP 404."""
        response = await client.delete("/api/v1/products/99999", headers=auth_headers)
        assert response.status_code == 404

    async def test_deleted_product_not_in_list(self, client, auth_headers, sample_product):
        """API-PROD-032: A deleted product does not appear in the product list."""
        await client.delete(f"/api/v1/products/{sample_product['id']}", headers=auth_headers)
        response = await client.get("/api/v1/products")
        data = response.json()
        ids = [p["id"] for p in data["items"]]
        assert sample_product["id"] not in ids

    async def test_double_delete_returns_404_on_second(self, client, auth_headers, sample_product):
        """API-PROD-033: Second delete of same product returns HTTP 404."""
        await client.delete(f"/api/v1/products/{sample_product['id']}", headers=auth_headers)
        response = await client.delete(
            f"/api/v1/products/{sample_product['id']}", headers=auth_headers
        )
        assert response.status_code == 404
