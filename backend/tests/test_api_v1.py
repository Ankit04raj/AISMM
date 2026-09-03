"""FastAPI API v1 integration tests."""

import pytest
import hmac
import hashlib
import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.security import create_access_token

client = TestClient(app)


@pytest.fixture(scope="module")
def auth_headers():
    """Return authenticated Bearer headers with a signed test JWT."""
    token = create_access_token(subject=str(uuid4()))
    return {"Authorization": f"Bearer {token}"}


def test_root_and_health_endpoints():
    """Test public health and root endpoints."""
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "AISMM Backend"

    resp_health = client.get("/health")
    assert resp_health.status_code == 200
    health_data = resp_health.json()
    assert "status" in health_data
    assert "instagram" in health_data["platforms"]


def test_platforms_endpoints(auth_headers):
    """Test /api/v1/platforms and capabilities."""
    resp = client.get("/api/v1/platforms", headers=auth_headers)
    assert resp.status_code == 200
    assert "instagram" in resp.json()["platforms"]

    resp_caps = client.get("/api/v1/platforms/instagram/capabilities", headers=auth_headers)
    assert resp_caps.status_code == 200
    caps = resp_caps.json()["capabilities"]
    assert "post_image" in caps
    assert "get_insights" in caps

    resp_unknown = client.get("/api/v1/platforms/non_existent/capabilities", headers=auth_headers)
    assert resp_unknown.status_code == 404


def test_auth_oauth_endpoints():
    """Test /api/v1/auth/oauth endpoints."""
    # Init OAuth
    init_payload = {
        "platform": "instagram",
        "redirect_uri": "http://localhost:8000/callback",
        "state": "test_state_123",
    }
    resp = client.post("/api/v1/auth/oauth/init", json=init_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "authorization_url" in data
    assert data["state"] == "test_state_123"

    # Unsupported platform
    resp_bad = client.post(
        "/api/v1/auth/oauth/init",
        json={"platform": "unsupported", "redirect_uri": "http://localhost:8000/callback"},
    )
    assert resp_bad.status_code == 400


def test_webhook_challenge_and_signature_verification():
    """Test Instagram webhook GET challenge and POST signature handling."""
    # 1. Challenge verification (GET)
    resp_challenge = client.get(
        "/api/v1/webhooks/instagram",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "challenge_code_999",
            "hub.verify_token": "webhook-secret-change-in-production",
        },
    )
    assert resp_challenge.status_code == 200
    assert resp_challenge.text == "challenge_code_999"

    # 2. Challenge with bad token
    resp_bad_token = client.get(
        "/api/v1/webhooks/instagram",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "code",
            "hub.verify_token": "wrong_token",
        },
    )
    assert resp_bad_token.status_code == 403

    # 3. Post webhook event with valid signature
    payload = json.dumps({
        "object": "instagram",
        "entry": [{
            "id": "12345",
            "time": 1725148800,
            "changes": [{
                "field": "comments",
                "value": {
                    "verb": "created",
                    "comment_id": "c_1",
                    "media_id": "m_1",
                    "text": "Awesome!",
                    "from": {"username": "user", "id": "u_1"}
                }
            }]
        }]
    }).encode("utf-8")

    secret = "webhook-secret-change-in-production"
    signature = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    resp_event = client.post(
        "/api/v1/webhooks/instagram",
        content=payload,
        headers={"x-hub-signature-256": signature, "Content-Type": "application/json"},
    )
    assert resp_event.status_code == 200
    assert resp_event.json()["status"] == "processed"


def test_comments_endpoints(auth_headers):
    """Test comments listing, reply, delete, and hide endpoints with mock adapter."""
    adapter = PlatformRegistry.get_adapter("instagram")
    with patch.object(adapter, "get_comments", new_callable=AsyncMock) as mock_get_comments, \
         patch.object(adapter, "reply_to_comment", new_callable=AsyncMock) as mock_reply, \
         patch.object(adapter, "delete_comment", new_callable=AsyncMock) as mock_delete, \
         patch.object(adapter, "hide_comment", new_callable=AsyncMock) as mock_hide:

        mock_comm = MagicMock()
        mock_comm.id = "c_101"
        mock_comm.text = "Hello comment"
        mock_comm.author_name = "testuser"
        mock_comm.author_id = "u_101"
        mock_comm.created_at = datetime.now(timezone.utc)
        mock_comm.is_hidden = False
        mock_comm.platform_data = {}
        mock_get_comments.return_value = [mock_comm]

        resp = client.get("/api/v1/comments/posts/instagram/post_123", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["comments"]) == 1
        assert data["comments"][0]["id"] == "c_101"

        # Reply
        reply_mock = MagicMock()
        reply_mock.id = "reply_202"
        reply_mock.text = "Thank you!"
        reply_mock.created_at = datetime.now(timezone.utc)
        reply_mock.platform_data = {}
        mock_reply.return_value = reply_mock

        resp_reply = client.post(
            "/api/v1/comments/instagram/c_101/reply",
            json={"text": "Thank you!"},
            headers=auth_headers,
        )
        assert resp_reply.status_code == 200
        assert resp_reply.json()["id"] == "reply_202"

        # Delete
        mock_delete.return_value = True
        resp_del = client.delete("/api/v1/comments/instagram/c_101", headers=auth_headers)
        assert resp_del.status_code == 200
        assert resp_del.json()["deleted"] is True

        # Hide
        mock_hide.return_value = True
        resp_hide = client.post("/api/v1/comments/instagram/c_101/hide", headers=auth_headers)
        assert resp_hide.status_code == 200
        assert resp_hide.json()["hidden"] is True
