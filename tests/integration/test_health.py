"""Integration tests for the health endpoint.

Test IDs: API-HEALTH-001 through API-HEALTH-003
"""


class TestHealthEndpoint:
    """API-HEALTH-001 to API-HEALTH-003: GET /health."""

    async def test_health_returns_200(self, client):
        """API-HEALTH-001: GET /health returns HTTP 200."""
        response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_returns_ok_status(self, client):
        """API-HEALTH-002: Response body contains status='ok'."""
        response = await client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    async def test_health_response_schema(self, client):
        """API-HEALTH-003: Response includes app and version fields."""
        response = await client.get("/health")
        data = response.json()
        assert "app" in data
        assert "version" in data
        assert isinstance(data["app"], str)
        assert isinstance(data["version"], str)
