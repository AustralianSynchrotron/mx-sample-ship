import os


class Config(object):
    SECRET_KEY = os.environ['SECRET_KEY']
    CACHE_TYPE = None


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost:4999'
    PUCKTRACKER_URL = 'http://localhost:8002'
    PORTAL_USERNAME = None
    PORTAL_PASSWORD = None
    PORTAL_URL = 'http://mxshiptestingportal/'


class FunctionalTestingConfig(TestingConfig):
    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True
    PUCKTRACKER_URL = os.environ.get('PUCKTRACKER_DEV_URL',
                                     'http://localhost:8000')
    PORTAL_USERNAME = os.environ.get('PORTAL_DEV_USERNAME')
    PORTAL_PASSWORD = os.environ.get('PORTAL_DEV_PASSWORD')
    PORTAL_URL = os.environ.get('PORTAL_DEV_URL',
                                'http://localhost:7000/api/v1')


class ProductionConfig(Config):
    PUCKTRACKER_URL = os.environ.get('PUCKTRACKER_URL')
    PORTAL_USERNAME = os.environ.get('PORTAL_USERNAME')
    PORTAL_PASSWORD = os.environ.get('PORTAL_PASSWORD')
    PORTAL_URL = 'https://portal.synchrotron.org.au/api/v1'


config = {
    'testing': TestingConfig,
    'functional-testing': FunctionalTestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
