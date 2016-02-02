from mxsampleship import create_app, mongo
from flask import url_for
import pytest
from threading import Thread


def empty_collections(mongo):
    for name in ['adaptors', 'dewars', 'ports', 'pucks']:
        mongo.db[name].remove()


@pytest.yield_fixture(scope='module', autouse=True)
def app():
    app = create_app('functional-testing')
    context = app.app_context()
    context.push()
    empty_collections(mongo)
    thread = Thread(target=app.run)
    thread.daemon = True
    thread.start()
    yield app
    context.pop()


def test_user_can_submit_form(browser):
    browser.visit(url_for('main.shipment_form'))
    browser.fill('username', 'jane')
    browser.fill('password', 'secret')
    browser.find_by_name('submit').first.click()
    assert browser.url == url_for('main.shipment_form')
    browser.find_by_name('submit').first.click()
    assert browser.is_text_present('The Dewar ID is: d-123a-1')
