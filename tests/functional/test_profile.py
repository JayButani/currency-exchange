from requests.auth import _basic_auth_str
from . import login

def test_profile_page(test_client):
    cu = login(test_client, 'jay@gmail.com', 'asdfasdf')
    response = test_client.get('/profile')
    assert response.status_code == 200
    assert b"Currency Exchange" in response.data
    assert b"Profile" in response.data
    assert b"Name" in response.data
    assert b"Default Currency" in response.data

def test_profile_update(test_client):
    cu = login(test_client, 'jay@gmail.com', 'asdfasdf')
    response = test_client.post('/profile', headers={"Authorization":  _basic_auth_str('jay@gmail.com','asdfasdf')},
        data = dict(name = 'JayA', default_currency = 'INR'), follow_redirects=True
    )
    assert b"Profile has been updated!" in response.data
    