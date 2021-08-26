from . import login

def test_login_page_with_fixture(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b"KOKO Networks" in response.data
    assert b"Login" in response.data
    assert b"Email Address" in response.data
    assert b"Password" in response.data


def test_login_page_post_without_data(test_client):
    """
    GIVEN a Flask application
    WHEN the '/login' page is is posted to (POST)
    THEN check that a '200' status code is returned and Email does not exits
    """
    response = test_client.post('/login')
    assert response.status_code == 200
    assert b"Email does not exist." in response.data

def test_login(test_client):
    """Make sure login and logout works."""

    response = login(test_client, 'aa@gmail.com', 'b')
    assert b"Email does not exist." in response.data

    response = login(test_client, 'jay@gmail.com', 'b')
    assert b"Incorrect password, try again." in response.data

    response = login(test_client, 'jay@gmail.com', 'asdfasdf')
    assert b"Logged in successfully!" in response.data

    assert response.status_code == 200

def test_logout(test_client):
    response = test_client.get('/logout', follow_redirects=True)

    assert b"KOKO Networks" in response.data
    assert b"Login" in response.data
    assert b"Email Address" in response.data
    assert b"Password" in response.data
    assert response.status_code == 200