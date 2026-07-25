from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "page-pulse",
    }


def test_invalid_url():
    response = client.post(
        "/api/v1/audits",
        json={"url": "not-a-valid-url"},
    )

    assert response.status_code == 422


@patch("app.api.routes.audits.fetch_url", new_callable=AsyncMock)
def test_successful_audit(mock_fetch):
    mock_fetch.return_value.status_code = 200
    mock_fetch.return_value.response_time_ms = 120
    mock_fetch.return_value.content_type = "text/html"
    mock_fetch.return_value.content_length = 1024

    response = client.post(
        "/api/v1/audits",
        json={"url": "https://success-test.example.com"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["cached"] is False
    assert data["audit"]["status_code"] == 200
    assert "request_id" in data


@patch("app.api.routes.audits.fetch_url", new_callable=AsyncMock)
def test_cache_returns_cached_result(mock_fetch):
    mock_fetch.return_value.status_code = 200
    mock_fetch.return_value.response_time_ms = 100
    mock_fetch.return_value.content_type = "text/html"
    mock_fetch.return_value.content_length = 500

    url = "https://cache-test.example.com"

    first_response = client.post(
        "/api/v1/audits",
        json={"url": url},
    )

    second_response = client.post(
        "/api/v1/audits",
        json={"url": url},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert first_response.json()["cached"] is False
    assert second_response.json()["cached"] is True

    assert mock_fetch.await_count == 1


@patch("app.api.routes.audits.fetch_url", new_callable=AsyncMock)
def test_fetch_timeout(mock_fetch):
    from app.exceptions.fetch_exceptions import FetchTimeoutError

    mock_fetch.side_effect = FetchTimeoutError(
        "The request timed out."
    )

    response = client.post(
        "/api/v1/audits",
        json={"url": "https://timeout-test.example.com"},
    )

    assert response.status_code == 504

    data = response.json()

    assert data["detail"]["code"] == "FETCH_TIMEOUT"
    assert "request_id" in data["detail"]


@patch("app.api.routes.audits.fetch_url", new_callable=AsyncMock)
def test_connection_failure(mock_fetch):
    from app.exceptions.fetch_exceptions import ConnectionFailedError

    mock_fetch.side_effect = ConnectionFailedError(
        "Connection failed."
    )

    response = client.post(
        "/api/v1/audits",
        json={"url": "https://connection-test.example.com"},
    )

    assert response.status_code == 502

    data = response.json()

    assert data["detail"]["code"] == "CONNECTION_FAILED"
    assert "request_id" in data["detail"]


def test_rate_limit():
    url = "https://rate-limit-test.example.com"

    responses = []

    for _ in range(61):
        response = client.post(
            "/api/v1/audits",
            json={"url": url},
        )

        responses.append(response)

    assert responses[-1].status_code == 429

    data = responses[-1].json()

    assert data["detail"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "request_id" in data["detail"]