from portalapi.models import Scientist, Visit
import pytest
from pytz import UTC
from datetime import datetime


def login_patch(auth, username=None, password=None):
    auth._token = '1a2b3c'
    auth._lifespan = 3600
    auth._expires = UTC.localize(datetime.now())
    return True


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
        Visit({'epn': '123a', 'start_time': '2016-04-29T08:00:00+10:00'}),
        Visit({'epn': '456b', 'start_time': '2016-05-01T08:00:00+10:00'}),
    ]
    return visits


@pytest.fixture(autouse=True)
def patch_portal_api(monkeypatch):
    monkeypatch.setattr('portalapi.Authentication.login', login_patch)
    monkeypatch.setattr('portalapi.PortalAPI.get_scientist', get_scientist_patch)
    monkeypatch.setattr('portalapi.PortalAPI.get_scientist_visits',
                        get_scientist_visits_patch)
