from app import create_app, mongo
from flask import url_for
import pytest

def empty_collections(mongo):
    for name in ['adaptors', 'dewars', 'ports', 'pucks']:
        mongo.db[name].remove()


@pytest.fixture()
def app(request):
    app = create_app('testing')
    context = app.app_context()
    context.push()
    empty_collections(mongo)
    def teardown():
        context.pop()
    request.addfinalizer(teardown)
    return app


def test_index_renders(app):
    client = app.test_client()
    response = client.get(url_for('main.index'))
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert '<title>MX Sample Shipment</title>' in html
    assert 'Full Name' in html


def test_form_submits(app):
    client = app.test_client()
    data = {
        'name': 'Jane',
    }
    response = client.post(url_for('main.index'), data=data)
    assert response.status_code == 302
    dewars = list(mongo.db.dewars.find())
    assert len(dewars) == 1
    dewar = dewars[0]
    assert dewar['owner'] == 'Jane'
