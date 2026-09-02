import pytest
from fastapi.testclient import TestClient

import main
from main import app, todos_db, users_db

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    """Return a TestClient and ensure both in-memory stores are cleared
    before (and after) every test so tests remain fully isolated."""
    users_db.clear()
    todos_db.clear()
    with TestClient(app) as c:
        yield c
    users_db.clear()
    todos_db.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def register_and_login(client, username="testuser", password="testpass"):
    client.post("/auth/register", json={"username": username, "password": password})
    response = client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return response.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Registration tests
# ---------------------------------------------------------------------------


def test_register_new_user(client):
    response = client.post("/auth/register", json={"username": "alice", "password": "secret"})
    assert response.status_code == 201
    assert response.json()["username"] == "alice"
    assert "user_id" in response.json()


def test_register_duplicate_user(client):
    client.post("/auth/register", json={"username": "bob", "password": "pass"})
    response = client.post("/auth/register", json={"username": "bob", "password": "pass"})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Login tests
# ---------------------------------------------------------------------------


def test_login_valid_credentials(client):
    client.post("/auth/register", json={"username": "carol", "password": "mypass"})
    response = client.post(
        "/auth/login",
        data={"username": "carol", "password": "mypass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        data={"username": "nobody", "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Protected endpoint tests
# ---------------------------------------------------------------------------


def test_todos_requires_auth(client):
    response = client.get("/todos")
    assert response.status_code == 401


def test_authenticated_user_can_create_and_list_todos(client):
    token = register_and_login(client, "dave", "davepass")
    headers = auth_headers(token)
    client.post("/todos", json={"title": "Dave's todo"}, headers=headers)
    response = client.get("/todos", headers=headers)
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 1
    assert todos[0]["title"] == "Dave's todo"


def test_users_cannot_see_each_others_todos(client):
    token_a = register_and_login(client, "userA", "passA")
    token_b = register_and_login(client, "userB", "passB")
    client.post("/todos", json={"title": "A's todo"}, headers=auth_headers(token_a))
    response = client.get("/todos", headers=auth_headers(token_b))
    assert response.status_code == 200
    assert response.json() == []


def test_user_cannot_delete_another_users_todo(client):
    token_a = register_and_login(client, "ownerUser", "passA")
    token_b = register_and_login(client, "attackerUser", "passB")
    create_resp = client.post("/todos", json={"title": "Owner's todo"}, headers=auth_headers(token_a))
    todo_id = create_resp.json()["id"]
    response = client.delete(f"/todos/{todo_id}", headers=auth_headers(token_b))
    assert response.status_code == 403


def test_user_cannot_update_another_users_todo(client):
    token_a = register_and_login(client, "ownerUser2", "passA")
    token_b = register_and_login(client, "attackerUser2", "passB")
    create_resp = client.post("/todos", json={"title": "Owner's todo"}, headers=auth_headers(token_a))
    todo_id = create_resp.json()["id"]
    response = client.put(f"/todos/{todo_id}", json={"title": "Hijacked"}, headers=auth_headers(token_b))
    assert response.status_code == 403


def test_get_todo_not_found(client):
    token = register_and_login(client, "eve", "evepass")
    response = client.get("/todos/nonexistent-id", headers=auth_headers(token))
    assert response.status_code == 404


def test_delete_todo_not_found(client):
    token = register_and_login(client, "frank", "frankpass")
    response = client.delete("/todos/nonexistent-id", headers=auth_headers(token))
    assert response.status_code == 404


def test_create_todo_requires_auth(client):
    response = client.post("/todos", json={"title": "No auth"})
    assert response.status_code == 401


def test_authenticated_user_can_update_own_todo(client):
    token = register_and_login(client, "grace", "gracepass")
    headers = auth_headers(token)
    create_resp = client.post("/todos", json={"title": "Original"}, headers=headers)
    todo_id = create_resp.json()["id"]
    update_resp = client.put(f"/todos/{todo_id}", json={"title": "Updated", "completed": True}, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated"
    assert update_resp.json()["completed"] is True


def test_authenticated_user_can_delete_own_todo(client):
    token = register_and_login(client, "heidi", "heidipass")
    headers = auth_headers(token)
    create_resp = client.post("/todos", json={"title": "To delete"}, headers=headers)
    todo_id = create_resp.json()["id"]
    delete_resp = client.delete(f"/todos/{todo_id}", headers=headers)
    assert delete_resp.status_code == 204
    # Confirm it's gone
    get_resp = client.get("/todos", headers=headers)
    assert get_resp.json() == []
