import os


class Config(object):
    SECRET_KEY = os.environ['SECRET_KEY']


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    MONGO_URI = 'mongodb://localhost/pucktracker_testing'


class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_URI = 'mongodb://localhost/pucktracker_dev'


class ProductionConfig(Config):
    MONGO_URI = os.environ.get('SAMPLE_SHIP_DB')



config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
