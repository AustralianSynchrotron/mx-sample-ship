from mxsampleship import create_app, mongo
from flask import url_for
import pytest

@pytest.yield_fixture
def app():
    app = create_app('testing')
    context = app.app_context()
    context.push()
    yield app
    context.pop()


def test_login_renders(app):
    client = app.test_client()
    response = client.get(url_for('auth.login'))
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Login' in html
    assert 'Username' in html
