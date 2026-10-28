"""Security-oriented tests for the TestForge Store API.

Test IDs: SEC-001 through SEC-015
These tests verify input safety, access control, and that errors
do not leak sensitive implementation details.
"""



class TestInputValidationSecurity:
    """SEC-001 to SEC-005: Reject dangerous or unexpected inputs safely."""

    async def test_extremely_long_name_returns_422(self, client, auth_headers):
        """SEC-001: A name exceeding the 200-char limit is rejected at schema level."""
        long_name = "A" * 300
        response = await client.post(
            "/api/v1/products",
            json={"name": long_name, "price": 1.0, "stock": 1, "category": "misc"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_sql_injection_in_name_rejected_or_handled_safely(self, client, auth_headers):
        """SEC-002: SQL-injection-style input in name is stored/rejected safely.

        Because we use SQLAlchemy with parameterised queries, this string
        must never cause a database error; it is either stored as a literal
        string or rejected by schema validation.
        """
        sql_injection = "'; DROP TABLE products; --"
        response = await client.post(
            "/api/v1/products",
            json={"name": sql_injection, "price": 1.0, "stock": 1, "category": "misc"},
            headers=auth_headers,
        )
        # The name is valid-length so may be stored as a literal — that is safe.
        # The important thing is that the server does NOT return 500.
        assert response.status_code in (201, 422)
        assert response.status_code != 500

    async def test_extremely_large_page_size_rejected(self, client):
        """SEC-003: An extremely large page_size is bounded by FastAPI query validation."""
        response = await client.get("/api/v1/products?page_size=1000000")
        assert response.status_code == 422

    async def test_non_integer_product_id_returns_422(self, client):
        """SEC-004: A non-integer product ID in the URL returns 422."""
        response = await client.get("/api/v1/products/not-an-id")
        assert response.status_code == 422

    async def test_extra_json_fields_ignored(self, client, auth_headers):
        """SEC-005: Extra fields in the request body are silently ignored."""
        response = await client.post(
            "/api/v1/products",
            json={
                "name": "Extra Widget",
                "price": 1.0,
                "stock": 1,
                "category": "misc",
                "admin_override": True,  # should be ignored
                "internal_id": "secret-42",
            },
            headers=auth_headers,
        )
        # Should succeed and not expose the extra fields in response
        assert response.status_code == 201
        data = response.json()
        assert "admin_override" not in data
        assert "internal_id" not in data


class TestAccessControl:
    """SEC-006 to SEC-010: Authorization enforcement."""

    async def test_expired_or_invalid_token_returns_401(self, client):
        """SEC-006: An obviously invalid token returns 401."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "Hack Widget", "price": 1.0, "stock": 1, "category": "misc"},
            headers={"Authorization": "Bearer eyJhbGciOiJub25lIn0.eyJzdWIiOiJoYWNrIn0."},
        )
        assert response.status_code == 401

    async def test_bearer_prefix_required(self, client):
        """SEC-007: Token without 'Bearer' prefix is rejected (401)."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "Hack Widget", "price": 1.0, "stock": 1, "category": "misc"},
            headers={"Authorization": "Token some.token.here"},
        )
        assert response.status_code == 401

    async def test_unauthenticated_cannot_modify_product(self, client, sample_product):
        """SEC-008: All write operations require authentication."""
        for method, url, body in [
            ("put", f"/api/v1/products/{sample_product['id']}", {"price": 1.0}),
            ("delete", f"/api/v1/products/{sample_product['id']}", None),
        ]:
            if method == "put":
                r = await client.put(url, json=body)
            else:
                r = await client.delete(url)
            assert r.status_code == 401, f"{method.upper()} {url} should require auth"

    async def test_orders_endpoint_requires_auth(self, client):
        """SEC-009: GET /orders requires authentication."""
        response = await client.get("/api/v1/orders")
        assert response.status_code == 401

    async def test_post_order_requires_auth(self, client, sample_product):
        """SEC-010: POST /orders requires authentication."""
        response = await client.post(
            "/api/v1/orders",
            json={"product_id": sample_product["id"], "quantity": 1},
        )
        assert response.status_code == 401


class TestErrorResponseSafety:
    """SEC-011 to SEC-015: Error responses must not leak sensitive details."""

    async def test_404_response_does_not_contain_stack_trace(self, client):
        """SEC-011: 404 error does not contain Python traceback."""
        response = await client.get("/api/v1/products/99999")
        body = response.text
        assert "Traceback" not in body
        assert "File " not in body

    async def test_401_response_contains_no_internal_detail(self, client):
        """SEC-012: 401 error response does not leak internal system paths."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "Widget", "price": 1.0, "stock": 1, "category": "misc"},
            headers={"Authorization": "Bearer bad.token.value"},
        )
        body = response.text
        assert "Traceback" not in body

    async def test_422_response_is_structured(self, client, auth_headers):
        """SEC-013: 422 response has structured 'detail' field, not a raw stack trace."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "", "price": 0, "stock": -1, "category": ""},
            headers=auth_headers,
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], list)

    async def test_nonexistent_endpoint_returns_404(self, client):
        """SEC-014: An unknown URL returns 404, not 500."""
        response = await client.get("/api/v1/nonexistent_endpoint")
        assert response.status_code == 404

    async def test_wrong_http_method_returns_405(self, client):
        """SEC-015: Wrong HTTP method returns 405, not 500."""
        response = await client.patch("/api/v1/products")
        assert response.status_code == 405
