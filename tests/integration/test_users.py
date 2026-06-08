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

async def test_admin_privilege(client: AsyncClient, admin_access_token):
    """ Test admin can list users. """

    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_access_token}"}
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

async def test_user_can_access_their_details(client: AsyncClient, registered_user):
    """ Test that users can access their own details. """

    response = await client.get(
        f"/api/v1/users/{registered_user['id']}",
        headers={"Authorization": f"Bearer {registered_user['access_token']}"}
    )

    print(response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == registered_user["id"]

async def test_admins_get_404_for_nonexisting_user(client: AsyncClient, admin_access_token):
    """ Test not found for a non-existent user. """

    response = await client.get(
        "/api/v1/users/99999",
        headers={"Authorization": f"Bearer {admin_access_token}"}
    )

    print(response.json())

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "NOT_FOUND"

async def test_user_cannot_access_other_users(client: AsyncClient, user_access_token):
    """ Test that users cannot access details of other users. """

    response = await client.get(
        "/api/v1/users/99999",
        headers={"Authorization": f"Bearer {user_access_token}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHORIZATION_FAILED"

async def test_user_update_own_profile(client: AsyncClient, registered_user):
    """ Test that users can update their profile. """

    response = await client.patch(
        f"/api/v1/users/{registered_user['id']}",
        json={"name": "New Name", "email":"newemail@test.com"},
        headers={"Authorization": f"Bearer {registered_user['access_token']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == registered_user["id"]
    assert data["name"] == "New Name"
    assert data["email"] == "newemail@test.com"

async def test_user_update_others_profile(client: AsyncClient, registered_user):
    """ Test that users cannot update other user's profile. """

    response = await client.patch(
        f"/api/v1/users/99999",
        json={"name": "New Name", "email":"newemail@test.com"},
        headers={"Authorization": f"Bearer {registered_user['access_token']}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHORIZATION_FAILED"

async def test_user_update_password_success(client: AsyncClient, registered_user):
    """ Test that users can update their passwords. """

    response = await client.patch(
        f"/api/v1/users/{registered_user['id']}/password",
        json={"old_password": "testpass123", "new_password": "newpassword@123"},
        headers={"Authorization": f"Bearer {registered_user['access_token']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == registered_user["id"]

async def test_user_cannot_update_password_other_user(client: AsyncClient, registered_user):
    """ Test that users cannot update other user's passwords. """

    response = await client.patch(
        f"/api/v1/users/99999/password",
        json={"old_password": "testpass123", "new_password": "newpassword@123"},
        headers={"Authorization": f"Bearer {registered_user['access_token']}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHORIZATION_FAILED"

async def test_admin_cannot_update_user_password(client: AsyncClient, registered_user, admin_access_token):
    """ Test that adminss cannot update other user's passwords. """

    response = await client.patch(
        f"/api/v1/users/{registered_user['id']}/password",
        json={"old_password": "testpass123", "new_password": "newpassword@123"},
        headers={"Authorization": f"Bearer {admin_access_token}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHORIZATION_FAILED"

async def test_admin_can_change_user_role(client: AsyncClient, registered_user, admin_access_token):
    """ Test that admins can change user's role. """

    response = await client.patch(
        f"/api/v1/users/{registered_user['id']}/role",
        json={"role_id": 2},
        headers={"Authorization": f"Bearer {admin_access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == registered_user["id"]

async def test_user_cannot_change_role(client: AsyncClient, registered_user):
    """ Test that users cannot change role. """

    response = await client.patch(
        f"/api/v1/users/{registered_user['id']}/role",
        json={"role_id": 2},
        headers={"Authorization": f"Bearer {registered_user['access_token']}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHORIZATION_FAILED"

async def test_admin_can_delete_user(client: AsyncClient, registered_user, admin_access_token):
    """ Test that admins can delete a user. """

    response = await client.delete(
        f"/api/v1/users/{registered_user['id']}",
        headers={"Authorization": f"Bearer {admin_access_token}"}
    )

    assert response.status_code == 204

async def test_user_cannot_delete_user(client: AsyncClient, registered_user):
    """ Test that users cannot delete users including themselves. """

    response = await client.delete(
        f"/api/v1/users/{registered_user['id']}",
        headers={"Authorization": f"Bearer {registered_user['access_token']}"}
    )

    assert response.status_code == 403
    data = response.json()
    assert "error" in data
    assert data["error"] == "AUTHORIZATION_FAILED"