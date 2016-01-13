import os


class Config(object):
    SECRET_KEY = os.environ['SECRET_KEY']


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    MONGO_URI = 'mongodb://localhost/pucktracker_testing'
    PORTAL_USERNAME = None
    PORTAL_PASSWORD = None
    PORTAL_URL = 'http://mxshiptestingportal/'


class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_URI = 'mongodb://localhost/pucktracker_dev'
    PORTAL_USERNAME = os.environ.get('PORTAL_DEV_USERNAME')
    PORTAL_PASSWORD = os.environ.get('PORTAL_DEV_PASSWORD')
    PORTAL_URL = os.environ.get('PORTAL_DEV_URL')


class ProductionConfig(Config):
    MONGO_URI = os.environ.get('SAMPLE_SHIP_DB')
    PORTAL_USERNAME = os.environ.get('PORTAL_USERNAME')
    PORTAL_PASSWORD = os.environ.get('PORTAL_PASSWORD')
    PORTAL_URL = os.environ.get('PORTAL_URL')


config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
