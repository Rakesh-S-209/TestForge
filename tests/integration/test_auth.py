"""Integration tests for authentication endpoints.

Test IDs: API-AUTH-001 through API-AUTH-015
"""



class TestRegistration:
    """API-AUTH-001 to API-AUTH-005: POST /api/v1/auth/register."""

    async def test_register_new_user_returns_201(self, client):
        """API-AUTH-001: Registering a new user returns HTTP 201."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"username": "alice", "email": "alice@example.com", "password": "password123"},
        )
        assert response.status_code == 201

    async def test_register_response_has_user_fields(self, client):
        """API-AUTH-002: Registration response contains id, username, email, is_active."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"username": "bob", "email": "bob@example.com", "password": "password123"},
        )
        data = response.json()
        assert data["username"] == "bob"
        assert data["email"] == "bob@example.com"
        assert data["is_active"] is True
        assert "id" in data

    async def test_register_duplicate_username_returns_409(self, client, registered_user):
        """API-AUTH-003: Duplicate username returns HTTP 409."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "other@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 409

    async def test_register_duplicate_email_returns_409(self, client, registered_user):
        """API-AUTH-004: Duplicate email returns HTTP 409."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "differentuser",
                "email": "testuser@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 409

    async def test_register_invalid_email_returns_422(self, client):
        """API-AUTH-005: An invalid email format returns HTTP 422."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"username": "carol", "email": "not-an-email", "password": "password123"},
        )
        assert response.status_code == 422


class TestLogin:
    """API-AUTH-006 to API-AUTH-010: POST /api/v1/auth/login."""

    async def test_valid_login_returns_200(self, client, registered_user):
        """API-AUTH-006: Valid credentials return HTTP 200."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "securepassword123"},
        )
        assert response.status_code == 200

    async def test_login_returns_access_token(self, client, registered_user):
        """API-AUTH-007: Response contains access_token and token_type='bearer'."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "securepassword123"},
        )
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 10

    async def test_wrong_password_returns_401(self, client, registered_user):
        """API-AUTH-008: Wrong password returns HTTP 401."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    async def test_nonexistent_user_returns_401(self, client):
        """API-AUTH-009: Login attempt for non-existent user returns HTTP 401."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "ghost", "password": "anything"},
        )
        assert response.status_code == 401

    async def test_missing_password_returns_422(self, client):
        """API-AUTH-010: Missing password field returns HTTP 422."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser"},
        )
        assert response.status_code == 422


class TestAuthProtection:
    """API-AUTH-011 to API-AUTH-015: Protected endpoint access control."""

    async def test_create_product_without_token_returns_401(self, client):
        """API-AUTH-011: Creating a product without a token returns HTTP 401."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "Unauthorized Widget", "price": 1.0, "stock": 1, "category": "misc"},
        )
        assert response.status_code == 401

    async def test_create_product_with_invalid_token_returns_401(self, client):
        """API-AUTH-012: An invalid/forged token returns HTTP 401."""
        response = await client.post(
            "/api/v1/products",
            json={"name": "Forged Widget", "price": 1.0, "stock": 1, "category": "misc"},
            headers={"Authorization": "Bearer totally.fake.token"},
        )
        assert response.status_code == 401

    async def test_update_product_without_token_returns_401(self, client, sample_product):
        """API-AUTH-013: Updating a product without a token returns HTTP 401."""
        response = await client.put(
            f"/api/v1/products/{sample_product['id']}",
            json={"price": 5.0},
        )
        assert response.status_code == 401

    async def test_delete_product_without_token_returns_401(self, client, sample_product):
        """API-AUTH-014: Deleting a product without a token returns HTTP 401."""
        response = await client.delete(f"/api/v1/products/{sample_product['id']}")
        assert response.status_code == 401

    async def test_orders_without_token_returns_401(self, client):
        """API-AUTH-015: Listing orders without a token returns HTTP 401."""
        response = await client.get("/api/v1/orders")
        assert response.status_code == 401
