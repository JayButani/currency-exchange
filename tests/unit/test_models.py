from website.models import User

def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, password, and name fields are defined correctly
    """
    user = User(email='jay@gmail.com', password='04CTGNtM1d', name='Jay')
    print(user)
    assert user.email == 'jay@gmail.com'
    assert user.password != 'Test123'
    assert user.name == 'Jay'