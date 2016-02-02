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
    assert 'Username' in html
