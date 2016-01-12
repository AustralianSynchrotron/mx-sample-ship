from flask import Flask
from flask.ext.pymongo import PyMongo
from flask.ext.qrcode import QRcode
from flask.ext.bootstrap import Bootstrap
from config import config


mongo = PyMongo()
bootstrap = Bootstrap()
qrcode = QRcode()


def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    mongo.init_app(app)
    qrcode.init_app(app)
    bootstrap.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
