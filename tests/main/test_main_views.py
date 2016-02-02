from mxsampleship import create_app, mongo
from flask import url_for
import pytest
from bs4 import BeautifulSoup
from six import string_types


LOGIN_DATA = {'username': 'jane', 'password': 'secret'}


def empty_collections(mongo):
    for name in ['adaptors', 'dewars', 'ports', 'pucks']:
        mongo.db[name].remove()


@pytest.yield_fixture
def client():
    app = create_app('testing')
    context = app.app_context()
    context.push()
    empty_collections(mongo)
    yield app.test_client()
    context.pop()


@pytest.yield_fixture
def logged_in_client(client):
    client.post(url_for('auth.login'), data=LOGIN_DATA)
    yield client


def test_shipment_form_redirects_to_login(client):
    response = client.get(url_for('main.shipment_form'))
    assert response.status_code == 302


def test_shipment_form_renders_after_login(logged_in_client):
    response = logged_in_client.get(url_for('main.shipment_form'))
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    page = BeautifulSoup(response.data, 'html.parser')
    assert 'MX Sample Shipment' in page.title
    assert 'Full Name' in html
    epn_option = page.find(id='epn').option
    assert epn_option.text == '123a @ 2016-04-29 08:00'
    assert epn_option['value'] == '123a'


def test_form_submits(logged_in_client):
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
        'epn': '123a',
        'return_dewar': 'y',
        'courier': 'Fast Deliveries',
        'courier_account': '999',
        'container_type': 'pucks',
        'container_ids_1': 'ASP001,ASP002',
        'container_ids_2': 'ASP003',
    }
    response = logged_in_client.post(url_for('main.shipment_form'), data=data)
    assert response.status_code == 302
    dewars = list(mongo.db.dewars.find())
    assert len(dewars) == 1
    dewar = dewars[0]
    assert isinstance(dewar['shipment_id'], string_types)
    assert dewar['name'] == 'd-123a-1'
    assert dewar['epn'] == '123a'
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
    assert dewar['returnDewar'] is True
    assert dewar['courier'] == 'Fast Deliveries'
    assert dewar['courierAccount'] == '999'
    assert dewar['containerType'] == 'pucks'
    assert dewar['expectedContainers'] == 'ASP001,ASP002 | ASP003'


def test_shipment_view(logged_in_client):
    dewar = {
        'shipment_id': '1a',
        'name': 'd-123a-1',
        'epn': '123a',
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
    response = logged_in_client.get(url_for('main.shipment', shipment_id='1a'))
    html = response.data.decode('utf-8')
    assert 'The Dewar ID is: d-123a-1' in html
    assert '123 Main Road' in html
