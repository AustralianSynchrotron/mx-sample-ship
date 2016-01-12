from app import create_app
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


def test_index(app):
    client = app.test_client()
    index_page = client.get('/')
    assert '<title>MX Sample Shipment</title>' in index_page.data.decode('utf-8')
