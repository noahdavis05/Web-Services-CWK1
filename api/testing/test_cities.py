
def test_get_cities_by_id(client, as_admin):
    response = client.get("/city/id/1")

    assert response.status_code == 200
    assert response.json()["name"] == "london"

def test_post_cities(client, as_admin):
    response = client.post("/city", json={
        "name":"CITY",
        "latitude": 1.0,
        "longitude": 1.0
    })

    assert response.status_code == 201
    assert response.json()["name"] == "city"

def test_get_cities_by_name(client, as_admin):
    response = client.get("/city/name/london")

    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_put_cities(client, as_admin):
    response = client.put("/city/1", json={
        "name":"lon",
        "longitude": 1.0,
        "latitude": 1.0
    })

    assert response.status_code == 200
    assert response.json()["name"] == "lon"


def test_get_cities_non_existent(client, as_admin):
    response = client.get("/city/id/10000")

    assert response.status_code == 404

def test_get_cities_non_existent_2(client, as_admin):
    response = client.get("/city/name/random")

    assert response.status_code == 404