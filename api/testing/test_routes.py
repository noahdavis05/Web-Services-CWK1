
def test_get_routes_by_id(client, as_admin):
    response = client.get("/routes/1")

    assert response.status_code == 200
    assert response.json()["origin_station"]["city"]["name"] == "northampton"
    assert response.json()["destination_station"]["city"]["name"] == "liverpool"

def test_post_route(client, as_admin):
    response = client.post("/routes", json={
        "price": 100,
        "notes": "TEST ROUTE",
        "origin_station_id": 1,
        "destination_station_id": 2,
        "transport_mode_id": 1
    })

    assert response.status_code == 201
    assert response.json()["origin_station"]["city"]["name"] == "northampton"
    assert response.json()["destination_station"]["city"]["name"] == "liverpool"

