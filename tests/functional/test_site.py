from mxsampleship import create_app
from flask import url_for
import pytest
from selenium.webdriver.support.select import Select
from vcr import VCR
from threading import Thread
import os


pytestmark = pytest.mark.skipif('DISPLAY' not in os.environ,
                                reason='Display required')


vcr = VCR(cassette_library_dir='tests/fixtures/cassettes')


@pytest.yield_fixture
def logged_in_browser(browser):
    browser.visit(url_for('main.shipment_form'))
    browser.fill('username', 'jane')
    browser.fill('password', 'secret')
    browser.find_by_name('submit').first.click()
    yield browser


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
def test_user_can_submit_form(logged_in_browser, db):
    db.clear()
    browser = logged_in_browser
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
    for idx in range(8):
        browser.fill('pucks-%s' % idx, idx + 1)
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
    assert browser.find_by_id('epn').text == 'Samples related to experiment: 123a'
    assert browser.find_by_id('dewar').text == 'The Dewar ID is: d-123a-1'
    assert '1,2,3,4,5,6,7,8' in browser.find_by_id('containers').text


def test_user_can_log_out(logged_in_browser):
    logged_in_browser.find_by_text('Log out').first.click()
    assert logged_in_browser.url == url_for('auth.login')


@vcr.use_cassette()
def test_user_can_submit_form_with_other_epn(logged_in_browser):
    browser = logged_in_browser
    assert browser.find_by_name('other_epn').visible is False
    browser.select('epn', 'other')
    assert browser.find_by_name('other_epn').visible is True
    browser.fill('other_epn', 'valid-epn')
    browser.select('container_type', 'pucks')
    browser.find_by_name('submit').first.click()
    assert browser.is_text_present('Samples related to experiment: valid-epn')


def test_shows_correct_fields_for_each_container_type(logged_in_browser):
    browser = logged_in_browser
    browser.select('container_type', 'select')
    assert browser.find_by_id('pucks').visible is False
    assert browser.find_by_id('cassettes').visible is False
    assert browser.find_by_id('canes').visible is False
    browser.select('container_type', 'pucks')
    assert browser.find_by_id('pucks').visible is True
    assert browser.find_by_id('cassettes').visible is False
    assert browser.find_by_id('canes').visible is False
    browser.select('container_type', 'other-pucks')
    assert browser.find_by_id('pucks').visible is True
    assert browser.find_by_id('cassettes').visible is False
    assert browser.find_by_id('canes').visible is False
    browser.select('container_type', 'cassettes')
    assert browser.find_by_id('pucks').visible is False
    assert browser.find_by_id('cassettes').visible is True
    assert browser.find_by_id('canes').visible is False
    browser.select('container_type', 'canes')
    assert browser.find_by_id('pucks').visible is False
    assert browser.find_by_id('cassettes').visible is False
    assert browser.find_by_id('canes').visible is True


@vcr.use_cassette()
def test_user_can_submit_form_with_cassettes(logged_in_browser):
    browser = logged_in_browser
    browser.fill('owner', 'Jane Doe')
    browser.select('container_type', 'cassettes')
    browser.fill('cassettes-0', 'CAS001')
    browser.fill('cassettes-1', 'CAS002')
    browser.find_by_name('submit').first.click()
    assert 'CAS001,CAS002' in browser.find_by_id('containers').text


@vcr.use_cassette()
def test_user_can_submit_form_with_canes(logged_in_browser):
    browser = logged_in_browser
    browser.fill('owner', 'Jane Doe')
    browser.select('container_type', 'canes')
    browser.fill('canes', 'some great canes')
    browser.find_by_name('submit').first.click()
    assert 'some great canes' in browser.find_by_id('containers').text


@vcr.use_cassette()
def test_invalid_submission_preserves_container_type(logged_in_browser):
    browser = logged_in_browser
    browser.fill('owner', '')
    browser.select('container_type', 'pucks')
    browser.find_by_name('submit').click()
    select = Select(browser.driver.find_element_by_id('container_type'))
    assert select.first_selected_option.get_attribute('value') == 'pucks'
