from website.models import Currency
from requests.auth import _basic_auth_str
from . import login

def test_wallet_page(test_client):
    cu = login(test_client, 'jay@gmail.com', 'asdfasdf')
    response = test_client.get('/wallet')
    assert response.status_code == 200
    assert b"Currency Exchange" in response.data
    assert b"Balance" in response.data
    assert b"Add" in response.data
    assert b"Withdraw" in response.data
    assert b"Transfer" in response.data
    assert b"Transactions" in response.data

def test_wallet_add_page(test_client):
    cu = login(test_client, 'jay@gmail.com', 'asdfasdf')
    response = test_client.get('/wallet/add')
    assert response.status_code == 200
    assert b"Currency Exchange" in response.data
    assert b"Add to Wallet" in response.data
    assert b"Currency" in response.data
    assert b"Amount" in response.data

def test_wallet_add_page_post(test_client):
    cu = login(test_client, 'jay@gmail.com', 'asdfasdf')
    response = test_client.post('/wallet/add', headers={"Authorization":  _basic_auth_str('jay@gmail.com','asdfasdf')},
        data = dict(currency = 'INR', amount = '100'), follow_redirects=True
    )
    assert b"Your transaction is successful. Wallet Balance updated!" in response.data

def test_wallet_withdraw_page(test_client):
    cu = login(test_client, 'jay@gmail.com', 'asdfasdf')
    response = test_client.get('/wallet/withdraw')
    assert response.status_code == 200
    assert b"Currency Exchange" in response.data
    assert b"Withdraw from Wallet" in response.data
    assert b"Balance" in response.data
    assert b"Amount" in response.data

def test_wallet_withdraw_page_post(test_client):
    cu = login(test_client, 'jay@gmail.com', 'asdfasdf')
    response = test_client.post('/wallet/withdraw', headers={"Authorization":  _basic_auth_str('jay@gmail.com','asdfasdf')},
        data = dict(amount = '100'), follow_redirects=True
    )
    assert b"Your withdrawal is successful. Wallet Balance updated!" in response.data

def test_wallet_transfer_page(test_client):
    cu = login(test_client, 'jay@gmail.com', 'asdfasdf')
    response = test_client.get('/wallet/transfer')
    assert response.status_code == 200
    assert b"Currency Exchange" in response.data
    assert b"Transfer from Wallet" in response.data
    assert b"Select User" in response.data
    assert b"Currency" in response.data
    assert b"Amount" in response.data

def test_wallet_transfer_page_post(test_client):
    cu = login(test_client, 'jay@gmail.com', 'asdfasdf')
    response = test_client.post('/wallet/transfer', headers={"Authorization":  _basic_auth_str('jay@gmail.com','asdfasdf')},
        data = dict(receiver=11, currency='INR', amount = '100'), follow_redirects=True
    )
    assert b"Your money transferred successfully!" in response.data
