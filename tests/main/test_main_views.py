from mxsampleship import create_app
from portalapi.portalapi import RequestFailed
from flask import url_for
import pytest
import responses
from bs4 import BeautifulSoup
from six import string_types
import json


LOGIN_DATA = {'username': 'jane', 'password': 'secret'}


@pytest.yield_fixture
def client():
    app = create_app('testing')
    context = app.app_context()
    context.push()
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
    page = BeautifulSoup(response.data, 'html.parser')
    assert 'MX Sample Shipment' in page.title
    assert 'Full Name' in page.text
    epn_option = page.find(id='epn').option
    assert epn_option.text == '123a @ 2016-04-29 08:00'
    assert epn_option['value'] == '123a'


def test_shipment_form_renders_when_get_visits_endpoint_is_empty(logged_in_client,
                                                                 monkeypatch):
    def get_scientist_visits_patch(api):
        raise RequestFailed()
    monkeypatch.setattr('portalapi.PortalAPI.get_scientist_visits',
                        get_scientist_visits_patch)

    response = logged_in_client.get(url_for('main.shipment_form'))
    assert response.status_code == 200
    page = BeautifulSoup(response.data, 'html.parser')
    assert 'MX Sample Shipment' in page.h1


@responses.activate
def test_form_submits(logged_in_client):
    responses.add(responses.POST, 'http://localhost:8002/dewars/new',
                  json={'error': None, 'data': {'_id': '1a'}})
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
    assert response.location == url_for('main.shipment', shipment_id='1a')
    dewar = json.loads(responses.calls[0].request.body)
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


@responses.activate
def test_shipment_view(logged_in_client):
    dewar = {
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
    responses.add(responses.GET, 'http://localhost:8002/dewars/1a',
                  json={'error': None, 'data': dewar})
    response = logged_in_client.get(url_for('main.shipment', shipment_id='1a'))
    html = response.data.decode('utf-8')
    assert 'The Dewar ID is: d-123a-1' in html
    assert '123 Main Road' in html


def test_directed_to_login_if_token_invalid(logged_in_client, monkeypatch):
    def is_valid_patch(auth):
        return False
    monkeypatch.setattr('portalapi.Authentication.is_valid', is_valid_patch)
    response = logged_in_client.get(url_for('main.shipment_form'))
    assert response.status_code == 302


def test_should_display_a_logout_link_when_logged_in(logged_in_client):
    response = logged_in_client.get(url_for('main.shipment_form'))
    assert 'Log out' in response.data.decode('utf-8')


def test_should_not_display_logout_if_not_logged_in(client):
    response = client.get(url_for('auth.login'))
    assert 'Log out' not in response.data.decode('utf-8')
