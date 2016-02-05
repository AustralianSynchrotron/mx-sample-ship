from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.qrcode import QRcode
from flask.ext.bootstrap import Bootstrap
from .config import config


__version__ = '0.2.1'


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = None
bootstrap = Bootstrap()
qrcode = QRcode()


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    login_manager.init_app(app)
    qrcode.init_app(app)
    bootstrap.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/ship')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/ship')

    return app
