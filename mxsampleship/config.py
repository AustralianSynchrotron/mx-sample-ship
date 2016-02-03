import os


class Config(object):
    SECRET_KEY = os.environ['SECRET_KEY']


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost:4999'
    MONGO_URI = 'mongodb://localhost/pucktracker_testing'
    PORTAL_USERNAME = None
    PORTAL_PASSWORD = None
    PORTAL_URL = 'http://mxshiptestingportal/'


class FunctionalTestingConfig(TestingConfig):
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_URI = os.environ.get('SAMPLE_SHIP_DEV_DB',
                               'mongodb://localhost/pucktracker_dev')
    PORTAL_USERNAME = os.environ.get('PORTAL_DEV_USERNAME')
    PORTAL_PASSWORD = os.environ.get('PORTAL_DEV_PASSWORD')
    PORTAL_URL = os.environ.get('PORTAL_DEV_URL',
                                'http://localhost:7000/api/v1')


class ProductionConfig(Config):
    MONGO_URI = os.environ.get('SAMPLE_SHIP_DB')
    PORTAL_USERNAME = os.environ.get('PORTAL_USERNAME')
    PORTAL_PASSWORD = os.environ.get('PORTAL_PASSWORD')
    PORTAL_URL = 'https://portal.synchrotron.org.au/api/v1'


config = {
    'testing': TestingConfig,
    'functional-testing': FunctionalTestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
