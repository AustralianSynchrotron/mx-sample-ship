from app import create_app, mongo
from flask import url_for
import pytest

@pytest.fixture()
def app(request):
    app = create_app('testing')
    context = app.app_context()
    context.push()
    def teardown():
        context.pop()
    request.addfinalizer(teardown)
    return app


def test_login_renders(app):
    client = app.test_client()
    response = client.get(url_for('auth.login'))
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Login' in html
    assert 'Username' in html
