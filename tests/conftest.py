from portalapi.models import Scientist, Visit
from portalapi.authentication import AuthenticationFailed
from portalapi.portalapi import RequestFailed
from flask import current_app
import pytest
import requests
from pytz import UTC
from datetime import datetime, timedelta


def login_patch(auth, username=None, password=None):
    if ((username is None and password is None)
        or (username == 'jane' and password == 'secret')):
        auth._token = '1a2b3c'
        auth._lifespan = 3600
        auth._expires = UTC.localize(datetime.now() + timedelta(hours=1))
        return True
    raise AuthenticationFailed()


def get_scientist_patch(api):
    return Scientist({
        'first_names': 'Jane',
        'last_name': 'Doe',
        'organisation': {'name_long': 'Some University'},
        'telephone_number_1': '111-222-333',
        'email': 'jane@example.com',
    })


def get_scientist_visits_patch(api):
    visits = [
        Visit({
            'epn': '123a',
            'start_time': '2016-04-29T08:00:00+10:00',
            'end_time': '2016-04-29T16:00:00+10:00',
        }),
        Visit({
            'epn': '456b',
            'start_time': '2016-05-01T08:00:00+10:00',
            'end_time': '2016-05-01T16:00:00+10:00',
        }),
    ]
    return visits


def get_visit_patch(api, epn, is_epn=None):
    if epn == 'valid-epn':
        return Visit({
            'epn': 'valid-epn',
            'start_time': '2016-01-02T08:00:00+10:00',
            'end_time': '2016-01-03T08:00:00+10:00',
        })
    else:
        raise RequestFailed()


@pytest.fixture(autouse=True)
def patch_portal_api(monkeypatch):
    monkeypatch.setattr('portalapi.Authentication.login', login_patch)
    monkeypatch.setattr('portalapi.PortalAPI.get_scientist', get_scientist_patch)
    monkeypatch.setattr('portalapi.PortalAPI.get_scientist_visits',
                        get_scientist_visits_patch)
    monkeypatch.setattr('portalapi.PortalAPI.get_visit', get_visit_patch)


@pytest.yield_fixture
def db():
    yield PuckTracker()


class PuckTracker():
    @property
    def actions_url(self):
        return '%s/actions' % current_app.config['PUCKTRACKER_URL']

    def clear(self):
        requests.post(self.actions_url, json={'type': 'REMOVE_ALL'})

    def add_dewar(self, dewar):
        requests.post(self.actions_url, json={
            'type': 'ADD_DEWAR',
            'dewar': dewar,
        })
