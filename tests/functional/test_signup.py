def test_signup_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/signup' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/sign-up')
    assert response.status_code == 200
    assert b"Currency Exchange" in response.data
    assert b"Sign Up" in response.data
    assert b"Email Address" in response.data
    assert b"Name" in response.data
    assert b"Password" in response.data
    assert b"Password (Confirm)" in response.data

def test_signup_page_post_without_data(test_client):
    """
    GIVEN a Flask application
    WHEN the '/signup' page is is posted to (POST)
    THEN check that a '200' status code is returned and Email does not exits
    """
    response = test_client.post('/sign-up')
    assert response.status_code == 200
    assert b"Email must be greater than 3 characters." in response.data

def test_signup(test_client):
    """Make sure signup and logout works."""

    # response = signup(test_client, '11a@gmail.com', 'Jay', 'asdfasdf', 'asdfasdf')
    # assert b"Account created!" in response.data

    response = signup(test_client, 'jay@gmail.com', 'Jay', 'asdfasdf', 'asdfasdf')
    assert b"Email already exists." in response.data

    response = signup(test_client, '', 'Jay', 'asdfasdf', 'asdfasdf')    
    assert b"Email must be greater than 3 characters." in response.data

    response = signup(test_client, 'jayt@gmail.com', 'a', 'asdfasdf', 'asdfasdf')    
    assert b"Name must be greater than 1 character." in response.data

    response = signup(test_client, 'jayt@gmail.com', 'Jay', 'asdfasdf', 'asdf')
    assert b"Passwords don&#39;t match" in response.data

    response = signup(test_client, 'jayt@gmail.com', 'Jay', 'asdfa', 'asdfa')    
    assert b"Password must be at least 7 characters." in response.data
    
    assert response.status_code == 200

def signup(client, email, name, password1, password2):
    return client.post('/sign-up', data=dict(
        email=email,
        name=name,
        password1=password1,
        password2=password2
    ), follow_redirects=True)
