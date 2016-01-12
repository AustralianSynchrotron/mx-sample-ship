import os


class Config(object):
    SECRET_KEY = os.environ['SECRET_KEY']


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
