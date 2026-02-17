
def test_get_stations_by_id(client, as_admin):
    response = client.get("/stations/1")

    assert response.status_code == 200
    assert response.json()["name"] == "northampton town centre"

def test_post_station(client, as_admin):
    response = client.post("/stations", json = {
        "name":"test station",
        "city_id": 1
    })

    assert response.status_code == 201
    assert response.json()["name"] == "test station"
    assert response.json()["city"]["name"] == "london"

def test_post_as_user(client, as_user):
    response = client.post("/stations", json = {
        "name":"test station",
        "city_id": 1
    })

    assert response.status_code == 403