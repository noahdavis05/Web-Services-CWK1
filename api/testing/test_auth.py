
def test_signup(client):
    response = client.post("/auth/signup", json={
        "email": "student2@uni.ac.uk",
        "password": "password123"
    })
    
    assert response.status_code == 200
    assert response.json()["id"] == "mock-uuid-123"


def test_login(client):
    response = client.post("/auth/login", json={
        "email": "student2@uni.co.uk",
        "password": "password123"
    })

    assert response.status_code == 200
    assert response.json()["access_token"] == "fake-access-token"