from local_settings import LocalConfig

class BaseConfig(LocalConfig):

    DATABASE_URI = 'sqlite:///test3.db'
    SECRET_KEY = 'testing'
    COOKIE_TTL = 100060
    DEBUG = True


class ProductionConfig(BaseConfig):
    DATABASE_URI = 'mysql+pymysql://test:test@localhost:3306/test'
    DEBUG = False

class TestConfig(BaseConfig):
    DATABASE_URI = 'sqlite:///testing.db'

class DevConfig(BaseConfig):
    pass


configs = dict(
    production=ProductionConfig,
    dev=DevConfig,
    test=TestConfig
)
