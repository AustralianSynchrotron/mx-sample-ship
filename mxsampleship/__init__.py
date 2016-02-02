from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.pymongo import PyMongo
from flask.ext.qrcode import QRcode
from flask.ext.bootstrap import Bootstrap
from .config import config


__version__ = '0.1.1'


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mongo = PyMongo()
bootstrap = Bootstrap()
qrcode = QRcode()


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    login_manager.init_app(app)
    mongo.init_app(app)
    qrcode.init_app(app)
    bootstrap.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
