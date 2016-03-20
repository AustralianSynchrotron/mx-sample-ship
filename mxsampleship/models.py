from . import login_manager
from portalapi import PortalAPI, Authentication
from flask import current_app
from flask.ext.login import UserMixin
import json


@login_manager.user_loader
def load_user(data):
    user = User(token_data=json.loads(data))
    if user.auth.is_valid():
        return user


class User(UserMixin):

    def __init__(self, username=None, password=None, token_data=None):
        super(User, self).__init__()
        if token_data:
            self.auth = Authentication.from_token_data(token_data)
        else:
            api_username = current_app.config['PORTAL_USERNAME']
            api_password = current_app.config['PORTAL_PASSWORD']
            api_url = current_app.config['PORTAL_URL']
            self.auth = Authentication(api_username, api_password, api_url)
            self.auth.login(username, password)
        self.api = PortalAPI(self.auth)

    def get_id(self):
        return json.dumps(self.auth.to_token_data())
