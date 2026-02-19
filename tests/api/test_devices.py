import pytest

@pytest.mark.asyncio
async def test_create_device_and_check_audit_log(client):
    device_data = {
        "serial_number": "SN-2026-X",
        "model": "Dell Latitude",
        "category": "Laptop"
    }

    resp_create = await client.post("/devices/", json=device_data)
    assert resp_create.status_code == 201
    device_id = resp_create.json()["id"]

    resp_history = await client.get(f"/devices/{device_id}/history")

    assert resp_history.status_code == 200
    history = resp_history.json()
    assert len(history) == 1
    assert history[0]["action"] == "create"
    assert history[0]["target_model"] == "Device"
    assert history[0]["changes"]["new_state"]["serial_number"] == "SN-2026-X"