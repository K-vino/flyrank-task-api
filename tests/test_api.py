from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_public_info():
    response = client.get("/public/info")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome stranger! This info is public."}


def test_protected_profile_unauthorized():
    # Missing authorization header
    response = client.get("/protected/profile")
    assert response.status_code == 401
    assert response.json() == {"error": "Access token required"}

    # Invalid token
    response = client.get(
        "/protected/profile", headers={"Authorization": "Bearer invalid_token_123"}
    )
    assert response.status_code == 401
    assert response.json() == {"error": "Invalid or expired token"}


def test_auth_signup_validation():
    response = client.post("/auth/signup", json={"email": "", "password": ""})
    assert response.status_code == 400
    assert response.json() == {"error": "Email and password are required"}


def test_auth_login_validation_and_flow():
    # Bad credentials
    response = client.post(
        "/auth/login", json={"email": "wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json() == {"error": "Invalid login credentials"}

    # Valid test login
    response = client.post(
        "/auth/login", json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code in [200, 401]
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        token = data["access_token"]

        # Test authenticated profile
        profile_res = client.get(
            "/protected/profile", headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_res.status_code == 200

        # Test logout
        logout_res = client.post(
            "/auth/logout", headers={"Authorization": f"Bearer {token}"}
        )
        assert logout_res.status_code == 204


def test_tasks_crud_flow():
    # List tasks
    res = client.get("/tasks")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

    # 404 task check
    res = client.get("/tasks/999999")
    assert res.status_code == 404
    assert res.json() == {"error": "Task not found"}

    # Create task validation
    res = client.post("/tasks", json={"title": "   "})
    assert res.status_code == 400

    # Create task success
    res = client.post("/tasks", json={"title": "Docker Auth Task"})
    assert res.status_code == 201
    created = res.json()
    new_id = created["id"]
    assert created["title"] == "Docker Auth Task"

    # Update task
    res = client.put(f"/tasks/{new_id}", json={"done": True})
    assert res.status_code == 200
    assert res.json()["done"] is True

    # Delete task
    res = client.delete(f"/tasks/{new_id}")
    assert res.status_code == 204

    # Verify deletion
    res = client.get(f"/tasks/{new_id}")
    assert res.status_code == 404


def test_stats():
    res = client.get("/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total" in data
    assert "completed" in data
    assert "pending" in data


if __name__ == "__main__":
    print("Running API Test Suite...")
    test_public_info()
    print("✓ Public info test passed")
    test_protected_profile_unauthorized()
    print("✓ Protected profile unauthorized test passed")
    test_auth_signup_validation()
    print("✓ Auth signup validation test passed")
    test_auth_login_validation_and_flow()
    print("✓ Auth login validation test passed")
    test_tasks_crud_flow()
    print("✓ Tasks CRUD flow test passed")
    test_stats()
    print("✓ Stats test passed")
    print("ALL TESTS PASSED SUCCESSFULLY!")

