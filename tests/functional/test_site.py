from mxsampleship import create_app
from flask import url_for
import pytest
from vcr import VCR
from threading import Thread
import os


pytestmark = pytest.mark.skipif('DISPLAY' not in os.environ,
				reason='Display required')


vcr = VCR(cassette_library_dir='tests/fixtures/cassettes')


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


@vcr.use_cassette()
def test_user_can_submit_form(browser):
    browser.visit(url_for('main.shipment_form'))
    browser.fill('username', 'jane')
    browser.fill('password', 'secret')
    browser.find_by_name('submit').first.click()
    assert browser.url == url_for('main.shipment_form')
    browser.fill('owner', 'Jane Doe')
    browser.fill('department', 'Chemistry')
    browser.fill('institute', 'Some University')
    browser.fill('street_address', '123 Main Road')
    browser.fill('city', 'Melbourne')
    browser.fill('state', 'VIC')
    browser.fill('postcode', '3000')
    browser.fill('country', 'Australia')
    browser.fill('phone', '123-456-789')
    browser.fill('email', 'jane@example.com')
    browser.select('epn', '123a')
    browser.check('return_dewar')
    browser.fill('courier', 'Fast Deliveries')
    browser.fill('courier_account', '122333')
    browser.select('container_type', 'pucks')
    browser.fill('container_ids_1', 'ASP0001,ASP0002,ASP0003,ASP0004')
    browser.fill('container_ids_2', 'ASP0006,ASP0007,ASP0008,ASP0009')
    browser.find_by_name('submit').first.click()
    assert browser.is_text_present('Jane Doe')
    assert browser.is_text_present('Chemistry')
    assert browser.is_text_present('Some University')
    assert browser.is_text_present('123 Main Road')
    assert browser.is_text_present('Melbourne')
    assert browser.is_text_present('VIC')
    assert browser.is_text_present('3000')
    assert browser.is_text_present('Australia')
    assert browser.is_text_present('Contact Phone: 123-456-789')
    assert browser.is_text_present('Contact Email: jane@example.com')
    assert browser.is_text_present('Samples related to experiment: 123a')
    assert browser.is_text_present('The Dewar ID is: d-123a-1')


def test_user_can_log_out(browser):
    browser.visit(url_for('main.shipment_form'))
    browser.fill('username', 'jane')
    browser.fill('password', 'secret')
    browser.find_by_name('submit').first.click()
    browser.find_by_text('Log out').first.click()
    assert browser.url == url_for('auth.login')

