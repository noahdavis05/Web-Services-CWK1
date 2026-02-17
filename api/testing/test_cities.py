
def test_get_cities(client, as_admin):
    response = client.get("/city/id/1")

    assert response.status_code == 200
    assert response.json()["name"] == "london"