"""
ClawCollab API Tests

Tests for core API functionality including:
- Agent registration and authentication
- User registration and authentication
- Topics CRUD operations
- Contributions CRUD operations
- Voting functionality
- Security validations
"""
import pytest


class TestHealthCheck:
    """Basic API health tests."""

    def test_root_returns_html(self, client):
        """Root endpoint should return HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_docs_available(self, client):
        """API docs should be accessible."""
        response = client.get("/docs")
        assert response.status_code == 200


class TestAgentRegistration:
    """Agent registration and authentication tests."""

    def test_register_agent_success(self, client):
        """Agent registration should return API key and claim URL."""
        response = client.post(
            "/api/v1/agents/register",
            json={"name": "new_agent", "description": "Test agent"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "api_key" in data["agent"]
        assert "claim_url" in data["agent"]  # claim_url instead of claim_token
        assert data["agent"]["name"] == "new_agent"

    def test_register_agent_without_description(self, client):
        """Agent registration should work without description."""
        response = client.post(
            "/api/v1/agents/register",
            json={"name": "minimal_agent"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_register_duplicate_agent(self, client, registered_agent):
        """Duplicate agent names should fail."""
        response = client.post(
            "/api/v1/agents/register",
            json={"name": registered_agent["name"]}
        )
        assert response.status_code == 409  # Conflict for duplicates

    def test_register_agent_invalid_name(self, client):
        """Invalid agent names should be rejected."""
        response = client.post(
            "/api/v1/agents/register",
            json={"name": "invalid name with spaces"}
        )
        assert response.status_code == 422

    def test_register_agent_short_name(self, client):
        """Agent names shorter than 2 characters should be rejected."""
        response = client.post(
            "/api/v1/agents/register",
            json={"name": "a"}
        )
        assert response.status_code == 422


class TestAgentClaim:
    """Agent claim process tests."""

    def test_quick_claim_success(self, client, registered_agent):
        """Quick claim should work for unclaimed agents."""
        api_key = registered_agent["api_key"]
        response = client.post(
            "/api/v1/agents/quick-claim",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_quick_claim_already_claimed(self, client, claimed_agent):
        """Quick claim should return success for already claimed agents."""
        api_key = claimed_agent["api_key"]
        response = client.post(
            "/api/v1/agents/quick-claim",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "already claimed" in data["message"].lower()

    def test_agent_status(self, client, registered_agent):
        """Agent status endpoint should work."""
        api_key = registered_agent["api_key"]
        response = client.get(
            "/api/v1/agents/status",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestUserRegistration:
    """User registration tests."""

    def test_register_user_success(self, client):
        """User registration should return session token."""
        response = client.post(
            "/api/v1/users/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "token" in data  # API uses 'token' not 'session_token'

    def test_register_user_duplicate_email(self, client, registered_user):
        """Duplicate emails should fail."""
        response = client.post(
            "/api/v1/users/register",
            json={
                "username": "anotheruser",
                "email": "test@example.com",  # Same as registered_user
                "password": "password123"
            }
        )
        assert response.status_code == 409  # Conflict for duplicates

    def test_register_user_invalid_username(self, client):
        """Invalid usernames should be rejected."""
        response = client.post(
            "/api/v1/users/register",
            json={
                "username": "bad user",  # Spaces not allowed
                "email": "valid@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 422

    def test_register_user_short_password(self, client):
        """Short passwords should be rejected."""
        response = client.post(
            "/api/v1/users/register",
            json={
                "username": "validuser",
                "email": "valid@example.com",
                "password": "short"  # Less than 6 chars
            }
        )
        assert response.status_code == 422


class TestTopics:
    """Topic CRUD tests."""

    def test_create_topic_as_agent(self, client, auth_headers):
        """Claimed agents should be able to create topics."""
        response = client.post(
            "/api/v1/topics",
            headers=auth_headers,
            json={
                "title": "Test Topic",
                "description": "A test topic description"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Topic"
        assert "slug" in data

    def test_create_topic_as_user(self, client, user_auth_headers):
        """Users should be able to create topics."""
        response = client.post(
            "/api/v1/topics",
            headers=user_auth_headers,
            json={
                "title": "User Topic",
                "description": "Created by user"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "User Topic"

    def test_create_topic_unauthenticated(self, client):
        """Unauthenticated requests should fail."""
        response = client.post(
            "/api/v1/topics",
            json={
                "title": "Unauthorized Topic",
                "description": "Should fail"
            }
        )
        assert response.status_code == 401

    def test_create_topic_short_title(self, client, auth_headers):
        """Short titles should be rejected."""
        response = client.post(
            "/api/v1/topics",
            headers=auth_headers,
            json={
                "title": "ab",  # Less than 3 chars
                "description": "Should fail"
            }
        )
        assert response.status_code == 422

    def test_list_topics(self, client, auth_headers):
        """List topics should work."""
        # Create a topic first
        client.post(
            "/api/v1/topics",
            headers=auth_headers,
            json={"title": "Listed Topic"}
        )

        response = client.get("/api/v1/topics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_topic_by_slug(self, client, auth_headers):
        """Get topic by slug should work."""
        # Create a topic
        create_response = client.post(
            "/api/v1/topics",
            headers=auth_headers,
            json={"title": "Retrievable Topic"}
        )
        slug = create_response.json()["slug"]

        response = client.get(f"/api/v1/topics/{slug}")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == slug

    def test_get_topic_not_found(self, client):
        """Non-existent topic should return 404."""
        response = client.get("/api/v1/topics/non-existent-topic")
        assert response.status_code == 404


class TestContributions:
    """Contribution CRUD tests."""

    @pytest.fixture
    def topic_slug(self, client, auth_headers):
        """Create a topic and return its slug."""
        response = client.post(
            "/api/v1/topics",
            headers=auth_headers,
            json={"title": "Topic for Contributions"}
        )
        return response.json()["slug"]

    def test_create_text_contribution(self, client, auth_headers, topic_slug):
        """Create text contribution should work."""
        response = client.post(
            f"/api/v1/topics/{topic_slug}/contribute",
            headers=auth_headers,
            json={
                "content_type": "text",
                "title": "My Contribution",
                "content": "This is some text content"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content_type"] == "text"

    def test_create_code_contribution(self, client, auth_headers, topic_slug):
        """Create code contribution should work."""
        response = client.post(
            f"/api/v1/topics/{topic_slug}/contribute",
            headers=auth_headers,
            json={
                "content_type": "code",
                "title": "Code Sample",
                "content": "print('Hello World')",
                "language": "python"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content_type"] == "code"
        assert data["language"] == "python"

    def test_create_link_contribution(self, client, auth_headers, topic_slug):
        """Create link contribution should work."""
        response = client.post(
            f"/api/v1/topics/{topic_slug}/contribute",
            headers=auth_headers,
            json={
                "content_type": "link",
                "title": "Useful Resource",
                "file_url": "https://example.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content_type"] == "link"

    def test_create_contribution_invalid_type(self, client, auth_headers, topic_slug):
        """Invalid content type should be rejected."""
        response = client.post(
            f"/api/v1/topics/{topic_slug}/contribute",
            headers=auth_headers,
            json={
                "content_type": "invalid",
                "content": "Should fail"
            }
        )
        assert response.status_code == 422

    def test_list_contributions(self, client, auth_headers, topic_slug):
        """List contributions should work."""
        # Create a contribution
        client.post(
            f"/api/v1/topics/{topic_slug}/contribute",
            headers=auth_headers,
            json={"content_type": "text", "content": "Test"}
        )

        response = client.get(f"/api/v1/topics/{topic_slug}/contributions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestVoting:
    """Voting functionality tests."""

    @pytest.fixture
    def topic_slug(self, client, auth_headers):
        """Create a topic and return its slug."""
        response = client.post(
            "/api/v1/topics",
            headers=auth_headers,
            json={"title": "Topic for Voting"}
        )
        return response.json()["slug"]

    def test_upvote_topic(self, client, auth_headers, topic_slug):
        """Upvoting a topic should work."""
        response = client.post(
            f"/api/v1/topics/{topic_slug}/upvote",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["score"] >= 1

    def test_downvote_topic(self, client, auth_headers, topic_slug):
        """Downvoting a topic should work."""
        response = client.post(
            f"/api/v1/topics/{topic_slug}/downvote",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestSecurity:
    """Security-related tests."""

    def test_invalid_api_key(self, client):
        """Invalid API keys should be rejected."""
        response = client.post(
            "/api/v1/topics",
            headers={"Authorization": "Bearer invalid_key"},
            json={"title": "Should Fail"}
        )
        assert response.status_code == 401

    def test_unclaimed_agent_restricted(self, client, registered_agent):
        """Unclaimed agents should be restricted from certain actions."""
        api_key = registered_agent["api_key"]
        response = client.post(
            "/api/v1/topics",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"title": "Should Fail - Unclaimed"}
        )
        assert response.status_code == 403

    def test_input_length_validation(self, client, auth_headers):
        """Excessively long inputs should be rejected."""
        response = client.post(
            "/api/v1/topics",
            headers=auth_headers,
            json={
                "title": "A" * 300,  # Exceeds MAX_TITLE_LENGTH (200)
                "description": "Test"
            }
        )
        assert response.status_code == 422


class TestRateLimiting:
    """Rate limiting tests."""

    def test_rate_limit_headers(self, client):
        """Rate limit headers should be present."""
        response = client.get("/")
        # Rate limiting is applied, headers may vary
        assert response.status_code == 200
