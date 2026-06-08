from httpx import AsyncClient


async def test_access_no_token(client: AsyncClient):
    """ Test access protected endpoint without a token. """

    response = await client.get(
        "/api/v1/users/1"
    )

    print(response.json())

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHENTICATION_FAILED"
    assert data["message"] == "Authorization header missing"

async def test_access_invalid_token(client: AsyncClient):
    """ Test access protected endpoint with invalid token. """

    response = await client.get(
        "/api/v1/users/1",
        headers={"Authorization": "Bearer invalidtoken"}
    )

    print(response.json())

    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHENTICATION_FAILED"
    assert data["message"] == "Invalid token"

async def test_admin_privilege(client: AsyncClient, admin_token):
    """ Test admin can list users. """

    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    print(response.json())

    assert response.status_code == 200
    data = response.json()
    assert "users" in data

async def test_user_privilege(client: AsyncClient, user_access_token):
    """ Test non-admin cannot list users """

    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {user_access_token}"}
    )

    print(response.json())

    assert response.status_code == 403
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHORIZATION_FAILED"
    assert data["message"] == "Admin privileges required"

async def test_existing_user(client: AsyncClient, user_access_token):
    """ Test to get an existing user. """

    response = await client.get(
        "/api/v1/users/1",
        headers={"Authorization": f"Bearer {user_access_token}"}
    )

    print(response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1

async def test_not_existing_user(client: AsyncClient, user_access_token):
    """ Test to get a non-existent user. """

    response = await client.get(
        "/api/v1/users/99999",
        headers={"Authorization": f"Bearer {user_access_token}"}
    )

    print(response.json())

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "NOT_FOUND"