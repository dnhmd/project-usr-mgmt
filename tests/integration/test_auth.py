from unittest.mock import patch

from httpx import AsyncClient


async def test_register_success(client: AsyncClient):
    """ Test that registration is successful. """

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "user@test.com",
            "password": "testpass123",
        }
    )

    print(response.json())

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_register_duplicate_email(client: AsyncClient, registered_user):
    """ Test that entered email is duplicate. """

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": registered_user["email"],
            "password": "testpass123",
        }
    )

    print(response.json())

    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"] == "VALIDATION_ERROR"
    assert "message" in data
    assert "Email already exists" in data["message"]

async def test_register_invalid_email_format(client: AsyncClient):
    """ Test that entered email is of the wrong format. """

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "thisisnotanemailaddress",
            "password": "testpass123",
        }
    )

    print(response.json())

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "VALIDATION_ERROR"
    assert "message" in data
    assert "Request validation failed" in data["message"]
    assert "value is not a valid email address: An email address must have an @-sign." in data["details"]["errors"][0]["msg"]

async def test_register_short_password(client: AsyncClient):
    """ Test that entered password is too short. """

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "user@test.com",
            "password": "2short",
        }
    )

    print(response.json())

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "VALIDATION_ERROR"
    assert "message" in data
    assert "Request validation failed" in data["message"]
    assert "String should have at least 8 characters" in data["details"]["errors"][0]["msg"]

async def test_login_success(client: AsyncClient, registered_user):
    """ Test that registration is successful. """

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        }
    )

    print(response.json())

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_login_wrong_email(client: AsyncClient, registered_user):
    """ Test that entered email is invalid. """

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@email.com",
            "password": registered_user["password"],
        }
    )

    print(response.json())

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHENTICATION_FAILED"

async def test_login_wrong_password(client: AsyncClient, registered_user):
    """ Test that entered password is wrong. """

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["email"],
            "password": "wrongpassword",
        }
    )

    print(response.json())

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHENTICATION_FAILED"

async def test_login_invalid_email_format(client: AsyncClient):
    """ Test that entered email is of the wrong format. """

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "thisisnotanemailaddress",
            "password": "testpass123",
        }
    )

    print(response.json())

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "VALIDATION_ERROR"
    assert "message" in data
    assert "Request validation failed" in data["message"]
    assert "value is not a valid email address: An email address must have an @-sign." in data["details"]["errors"][0]["msg"]

async def test_login_short_password(client: AsyncClient):
    """ Test that entered password is too short. """

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "name": "Test User",
            "email": "user@test.com",
            "password": "2short",
        }
    )

    print(response.json())

    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "VALIDATION_ERROR"
    assert "message" in data
    assert "Request validation failed" in data["message"]
    assert "String should have at least 8 characters" in data["details"]["errors"][0]["msg"]

async def test_refresh_success(client: AsyncClient, registered_user):
    """ Test that refresh request is successful. """

    response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": registered_user["refresh_token"] 
        }
    )

    print(response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"

async def test_refresh_invalid_token(client: AsyncClient):
    """ Test that refresh token provided is invalid. """

    response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": "invalidtoken" 
        }
    )

    print(response.json())

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHENTICATION_FAILED"

async def test_refresh_revoked_token(client: AsyncClient, registered_user):
    """ Test that refresh token provided is invalid. """

    refresh_token = registered_user["refresh_token"]

    # Revoking the refreshed token
    await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    # Should fail
    response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh_token 
        }
    )

    print(response.json())

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHENTICATION_FAILED"

async def test_forgot_password_success(client: AsyncClient, registered_user):
    """ Test that forgot password is successful. """

    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={
            "email": "user@test.com" 
        }
    )

    print(response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "If an account with that email exists, a reset link has been sent."

async def test_reset_password_success(client: AsyncClient, registered_user):
    """ Test that password reset is successful using a valid token. """

    with patch("builtins.print") as mock_print:
        await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": registered_user["email"]}
        )

        # Extract token from the printed URL
        printed_url = mock_print.call_args[0][0]
        token = printed_url.split("token=")[1]

        response = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": "newpass123"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Password reset is successful."

async def test_reset_password_invalid_token(client: AsyncClient, registered_user):
    """ Test that password reset fails using an invalid token. """

    await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": registered_user["email"]}
    )

    response = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": "invalidtoken", "new_password": "newpass123"}
    )

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHENTICATION_FAILED"