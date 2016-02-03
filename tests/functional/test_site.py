from mxsampleship import create_app
from flask import url_for
import pytest
import responses
from threading import Thread


@pytest.yield_fixture(scope='module', autouse=True)
def app():
    app = create_app('functional-testing')
    context = app.app_context()
    context.push()
    thread = Thread(target=app.run)
    thread.daemon = True
    thread.start()
    yield app
    context.pop()


def mock_pucktracker():
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
    responses.add(responses.POST, 'http://pucktracker-test/dewars/new',
                  json={'error': None, 'data': {'_id': '1a'}})
    responses.add(responses.GET, 'http://pucktracker-test/dewars/1a',
                  json={'error': None, 'data': dewar})



@responses.activate
def test_user_can_submit_form(browser):
    mock_pucktracker()
    browser.visit(url_for('main.shipment_form'))
    browser.fill('username', 'jane')
    browser.fill('password', 'secret')
    browser.find_by_name('submit').first.click()
    assert browser.url == url_for('main.shipment_form')
    browser.find_by_name('submit').first.click()
    assert browser.is_text_present('The Dewar ID is: d-123a-1')
