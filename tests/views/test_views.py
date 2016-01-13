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
        'owner': 'Jane',
        'department': 'Chemistry',
        'institute': 'Some University',
        'street_address': '123 Main Road',
        'city': 'Brisbane',
        'state': 'Queensland',
        'postcode': '3000',
        'country': 'Australia',
        'phone': '111-222-333',
        'email': 'jane@example.com',
        'epn': '123',
        'return_dewar': 'y',
        'courier': 'Fast Deliveries',
        'courier_account': '999',
        'container_type': 'pucks',
        'container_ids_1': 'ASP001,ASP002',
        'container_ids_2': 'ASP003',
    }
    response = client.post(url_for('main.index'), data=data)
    assert response.status_code == 302
    dewars = list(mongo.db.dewars.find())
    assert len(dewars) == 1
    dewar = dewars[0]
    assert isinstance(dewar['shipment_id'], str)
    assert dewar['name'] == 'd-123-1'
    assert dewar['epn'] == '123'
    assert dewar['owner'] == 'Jane'
    assert dewar['department'] == 'Chemistry'
    assert dewar['institute'] == 'Some University'
    assert dewar['streetAddress'] == '123 Main Road'
    assert dewar['city'] == 'Brisbane'
    assert dewar['state'] == 'Queensland'
    assert dewar['postcode'] == '3000'
    assert dewar['country'] == 'Australia'
    assert dewar['phone'] == '111-222-333'
    assert dewar['email'] == 'jane@example.com'
    assert dewar['returnDewar'] == True
    assert dewar['courier'] == 'Fast Deliveries'
    assert dewar['courierAccount'] == '999'
    assert dewar['containerType'] == 'pucks'
    assert dewar['expectedContainers'] == 'ASP001,ASP002 | ASP003'


def test_shipment_view(app):
    client = app.test_client()
    dewar = {
        'shipment_id': '1a',
        'name': 'd-123-1',
        'epn': '123',
        'owner': 'Jane',
        'department': 'Chemistry',
        'institute': 'Some University',
        'streetAddress': '123 Main Road',
        'city': 'Brisbane',
        'state': 'Queensland',
        'postcode': '3000',
        'country': 'Australia',
        'phone': '111-222-333',
        'email': 'jane@example.com',
        'returnDewar': True,
        'courier': 'Fast Deliveries',
        'courierAccount': '999',
        'containerType': 'pucks',
        'expectedContainers': 'ASP001,ASP002 | ASP003',
    }
    mongo.db.dewars.insert(dewar)
    response = client.get(url_for('main.shipment', shipment_id='1a'))
    html = response.data.decode('utf-8')
    assert 'The Dewar ID is: d-123-1' in html
    assert '123 Main Road' in html
