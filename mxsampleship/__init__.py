from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.qrcode import QRcode
from flask.ext.bootstrap import Bootstrap
from .config import config_lookup


__version__ = '0.3.2'


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = None
bootstrap = Bootstrap()
qrcode = QRcode()


def create_app(config_name):

    config = config_lookup[config_name]
    url_prefix = config.URL_PREFIX

    app = Flask(__name__, static_url_path=('%s/static' % url_prefix))
    app.config.from_object(config)

    login_manager.init_app(app)
    qrcode.init_app(app)
    bootstrap.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix=url_prefix)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix=url_prefix)

    return app
