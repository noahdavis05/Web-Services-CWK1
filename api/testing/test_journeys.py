
def test_routes_by_id(client, as_admin):
    response = client.get("/journeys/id?origin_id=8&destination_id=120")

    assert response.status_code == 200
    assert len(response.json()["path"]) == 1

def test_routes_by_name(client, as_admin):
    response = client.get("/journeys/name?origin_name=leeds&destination_name=bath")

    assert response.status_code == 200
    assert len(response.json()["path"]) == 1

def test_id_routes_railcard_discount(client, as_admin):
    response = client.get("/journeys/id?origin_id=8&destination_id=120&railcard_discount=30")

    assert response.status_code == 200
    assert response.json()["total_price"] == "70.0"
    assert response.json()["railcard_discounts"] == "30.0"
    assert response.json()["ticket_price"] == "100.0"

def test_id_routes_advanced_discount(client, as_admin):
    response = client.get("/journeys/id?origin_id=8&destination_id=120&advanced_fares=true")

    # co-ordinates are 139.81 miles apart
    # therefore advanced discount is 40%

    assert response.status_code == 200
    assert response.json()["total_price"] == "60.0"
    assert response.json()["railcard_discounts"] == "0.0"
    assert response.json()["ticket_price"] == "100.0"
    assert response.json()["advanced_discounts"] == "40.0"

def test_id_all_discounts(client, as_admin):
    response = client.get("/journeys/id?origin_id=8&destination_id=120&advanced_fares=true&railcard_discount=30")

    # co-ordinates are 139.81 miles apart
    # therefore advanced discount is 40%
    # railcard discount is calculated before the advanced discount
    # but doesn't actually matter what order as price will remain the same

    assert response.status_code == 200
    assert response.json()["total_price"] == "42.0"
    assert response.json()["railcard_discounts"] == "30.0"
    assert response.json()["ticket_price"] == "100.0"
    assert response.json()["advanced_discounts"] == "28.0"

def test_name_routes_railcard_discount(client, as_admin):
    response = client.get("/journeys/name?origin_name=leeds&destination_name=bath&railcard_discount=30")

    assert response.status_code == 200
    assert response.json()["total_price"] == "70.0"
    assert response.json()["railcard_discounts"] == "30.0"
    assert response.json()["ticket_price"] == "100.0"

def test_name_routes_advanced_discount(client, as_admin):
    response = client.get("/journeys/name?origin_name=leeds&destination_name=bath&advanced_fares=true")

    # co-ordinates are 139.81 miles apart
    # therefore advanced discount is 40%

    assert response.status_code == 200
    assert response.json()["total_price"] == "60.0"
    assert response.json()["railcard_discounts"] == "0.0"
    assert response.json()["ticket_price"] == "100.0"
    assert response.json()["advanced_discounts"] == "40.0"

def test_name_all_discounts(client, as_admin):
    response = client.get("/journeys/name?origin_name=leeds&destination_name=bath&advanced_fares=true&railcard_discount=30")

    # co-ordinates are 139.81 miles apart
    # therefore advanced discount is 40%
    # railcard discount is calculated before the advanced discount
    # but doesn't actually matter what order as price will remain the same

    assert response.status_code == 200
    assert response.json()["total_price"] == "42.0"
    assert response.json()["railcard_discounts"] == "30.0"
    assert response.json()["ticket_price"] == "100.0"
    assert response.json()["advanced_discounts"] == "28.0"

def test_id_complex_route_no_coach_limit(client, as_admin):
    response = client.get("/journeys/id?origin_id=86&destination_id=55&max_coach_legs=10")

    assert response.status_code == 200
    assert len(response.json()["path"]) == 3

def test_name_complex_route_no_coach_limit(client, as_admin):
    response = client.get("/journeys/name?origin_name=exeter&destination_name=aberdeen&max_coach_legs=10")

    assert response.status_code == 200
    assert len(response.json()["path"]) == 3

def test_id_complex_route_limit_coaches(client, as_admin):
    response = client.get("/journeys/id?origin_id=86&destination_id=55&max_coach_legs=2")

    print(response.json()["path"])

    assert response.status_code == 200
    assert len(response.json()["path"]) == 3
    assert response.json()["path"][2]["transport_mode"]["id"] == 2

def test_id_complex_route_limit_coaches_and_discounts(client, as_admin):
    response = client.get("/journeys/id?origin_id=86&destination_id=55&max_coach_legs=2&advanced_fares=true&railcard_discount=30")

    print(response.json()["path"])

    assert response.status_code == 200
    assert len(response.json()["path"]) == 3
    assert response.json()["path"][2]["transport_mode"]["id"] == 2
    assert response.json()["ticket_price"] == "114.0"
    assert response.json()["railcard_discounts"] == "30.0"
    assert response.json()["advanced_discounts"] == "28.0"
    assert response.json()["total_price"] == "56.0"

def test_name_complex_route_limit_coaches(client, as_admin):
    response = client.get("/journeys/name?origin_name=exeter&destination_name=aberdeen&max_coach_legs=2")

    print(response.json()["path"])

    assert response.status_code == 200
    assert len(response.json()["path"]) == 3
    assert response.json()["path"][2]["transport_mode"]["id"] == 2

def test_name_complex_route_limit_coaches_and_discounts(client, as_admin):
    response = client.get("/journeys/name?origin_name=exeter&destination_name=aberdeen&max_coach_legs=2&advanced_fares=true&railcard_discount=30")

    print(response.json()["path"])

    assert response.status_code == 200
    assert len(response.json()["path"]) == 3
    assert response.json()["path"][2]["transport_mode"]["id"] == 2
    assert response.json()["ticket_price"] == "114.0"
    assert response.json()["railcard_discounts"] == "30.0"
    assert response.json()["advanced_discounts"] == "28.0"
    assert response.json()["total_price"] == "56.0"

    
