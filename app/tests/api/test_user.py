import pytest

@pytest.mark.asyncio
async def test_create_user_success(client):
    payload = {
        "username": "jdoe",
        "full_name": "John Doe"
    }

    response = await client.post("/users/", json=payload)

    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == "jdoe"
    assert data["full_name"] == "John Doe"
    assert "id" in data
    assert isinstance(data["id"], int)

@pytest.mark.asyncio
async def test_get_all_users(client):
    await client.post("/users/", json={"username": "testuser", "full_name": "Test User"})

    response = await client.get("/users/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["username"] == "testuser"