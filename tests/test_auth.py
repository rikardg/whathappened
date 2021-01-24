from flask import session
from app.auth.models import User


def test_register(app, db):
    client = app.test_client()
    assert client.get('/auth/register').status_code == 200

    response = client.post(
        '/auth/register', data={'username': 'a',
                                'email': 't@t.com',
                                'password': 'b',
                                'password2': 'b'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    user = User.get(1)
    assert user.username == 'a'
    assert user.email == 't@t.com'


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
