
def test_get_transport_by_id(client, as_admin):
    response = client.get("/transport_mode/1")

    assert response.status_code == 200
    assert response.json()["name"] == "coach"

def test_post_transport(client, as_admin):
    response = client.post("/transport_mode", json={
        "name":"test transport"
    })

    assert response.status_code == 201
    assert response.json()["name"] == "test transport"