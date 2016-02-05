from mxsampleship import create_app
from flask import url_for
import pytest


@pytest.yield_fixture
def client():
    app = create_app('testing')
    context = app.app_context()
    context.push()
    yield app.test_client()
    context.pop()


def test_login_renders(client):
    response = client.get(url_for('auth.login'))
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Login' in html
    assert 'Email' in html


def test_login_reloads_on_failed_auth(client):
    invalid_login_data = {'username': 'jane', 'password': 'wrong'}
    response = client.post(url_for('auth.login'), data=invalid_login_data)
    assert response.status_code == 401
    assert 'Email or password incorrect' in response.data.decode('utf-8')
