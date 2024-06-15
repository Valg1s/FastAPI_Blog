from tests.conftest import client


def test_create_user():
    response = client.post(
        "/registration/",
        json={"username": "testuser1", "password": "testpassword"}
    )
    assert response.status_code == 201


def test_create_existing_user():
    client.post(
        "/registration/",
        json={"username": "testuser1", "password": "testpassword"}
    )

    response = client.post(
        "/registration/",
        json={"username": "testuser1", "password": "testpassword"}
    )
    assert response.status_code == 400


def test_login_user():
    client.post(
        "/registration/",
        json={"username": "testuser", "password": "testpassword"}
    )

    response = client.post(
        "/login/",
        data={"username": "testuser", "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password():
    response = client.post(
        "/login/",
        data={"username": "testuser", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


def test_login_nonexistent_user():
    response = client.post(
        "/login/",
        data={"username": "nonexistentuser", "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}
