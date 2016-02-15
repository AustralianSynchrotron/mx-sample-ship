from mxsampleship import create_app
from portalapi.portalapi import RequestFailed
from flask import url_for, current_app
import pytest
import responses
from bs4 import BeautifulSoup
from six import string_types
from six.moves.urllib.parse import urlsplit
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


def test_routes_should_have_url_prefix(client):
    assert urlsplit(url_for('main.index')).path == '/ship-test/'


def test_static_routes_should_have_url_prefix(client):
    url = url_for('static', filename='js/knockout.js')
    assert urlsplit(url).path == '/ship-test/static/js/knockout.js'


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
    new_dewar_url = '%s/dewars/new' % current_app.config['PUCKTRACKER_URL']
    responses.add(responses.POST, new_dewar_url,
                  json={'error': None, 'data': {'name': 'd-1a-1'}})
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
        'pucks-0': '1',
        'pucks-1': '2',
        'pucks-2': '3',
    }
    response = logged_in_client.post(url_for('main.shipment_form'), data=data)
    assert response.status_code == 302
    assert response.location == url_for('main.shipment', dewar_name='d-1a-1')
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
    assert dewar['expectedContainers'] == '1,2,3,,,,,'


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
        'expectedContainers': '1,2,3,4,5,,,',
    }
    responses.add(responses.GET,
                  '%s/dewars/d-1a-1' % current_app.config['PUCKTRACKER_URL'],
                  json={'error': None, 'data': dewar})
    response = logged_in_client.get(url_for('main.shipment', dewar_name='d-1a-1'))
    html = response.data.decode('utf-8')
    assert 'The Dewar ID is: d-123a-1' in html
    assert '123 Main Road' in html
    assert '1,2,3,4,5' in html


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


def test_displays_errors_if_form_entered_incorrectly(logged_in_client):
    data_missing_owner = {'owner': ''}
    response = logged_in_client.post(url_for('main.shipment_form'),
                                     data=data_missing_owner)
    page = BeautifulSoup(response.data, 'html.parser')
    assert 'This field is required.' in page.text


def test_email_is_required(logged_in_client):
    data_missing_email = {'owner': 'Jane'}
    response = logged_in_client.post(url_for('main.shipment_form'),
                                     data=data_missing_email)
    page = BeautifulSoup(response.data, 'html.parser')
    assert 'This field is required.' in page.text


def test_submitted_data_should_not_be_overwitten(logged_in_client):
    data_with_invalid_email = {'owner': 'John', 'email': 'invalid-email'}
    response = logged_in_client.post(url_for('main.shipment_form'),
                                     data=data_with_invalid_email)
    page = BeautifulSoup(response.data, 'html.parser')
    assert page.find(attrs={'name': 'owner'})['value'] == 'John'
    assert page.find(attrs={'name': 'email'})['value'] == 'invalid-email'
