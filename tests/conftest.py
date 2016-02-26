from portalapi.models import Scientist, Visit
from portalapi.authentication import AuthenticationFailed
from portalapi.portalapi import RequestFailed
from flask import current_app
import pytest
import requests
from pytz import UTC
from datetime import datetime, timedelta
from freezegun import freeze_time


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


def get_scientist_visits_patch(api, start_time=None, end_time=None):
    if start_time is None:
        start_time = UTC.localize(datetime.utcnow())
    if end_time is None:
        end_time = start_time + timedelta(days=1)
    visits = [
        Visit({
            'epn': '123a',
            'start_time': '2016-04-29T08:00:00+10:00',
            'end_time': '2016-04-29T16:00:00+10:00',
            'equipment_id': 23,
            'principal_scientist': {'email': 'john@example.com'},
        }),
        Visit({
            'epn': '456b',
            'start_time': '2016-06-01T08:00:00+10:00',
            'end_time': '2016-06-01T16:00:00+10:00',
        }),
    ]
    return [v for v in visits
            if v.start_time >= start_time and v.start_time <= end_time]


def get_visit_patch(api, epn, is_epn=None):
    if epn == 'valid-epn':
        return Visit({
            'epn': 'valid-epn',
            'start_time': '2016-01-02T08:00:00+10:00',
            'end_time': '2016-01-03T08:00:00+10:00',
        })
    else:
        raise RequestFailed()


@pytest.yield_fixture(autouse=True)
def patch_portal_api(monkeypatch):
    with freeze_time('2016-04-29T07:00:00+10:00'):
        monkeypatch.setattr('portalapi.Authentication.login', login_patch)
        monkeypatch.setattr('portalapi.PortalAPI.get_scientist', get_scientist_patch)
        monkeypatch.setattr('portalapi.PortalAPI.get_scientist_visits',
                            get_scientist_visits_patch)
        monkeypatch.setattr('portalapi.PortalAPI.get_visit', get_visit_patch)
        yield


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
