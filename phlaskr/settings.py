import os
from local_settings import LocalConfig

class BaseConfig(LocalConfig):

    DATABASE_URI = 'sqlite:///test3.db'
    SECRET_KEY = 'testing'
    COOKIE_TTL = 100060
    DEBUG = True


class ProductionConfig(BaseConfig):
    DATABASE_URI = 'postgres://boayqxuajzoyaz:7dI-lm3A028GIqWwgdY1LsHAl6@ec2-54-227-247-161.compute-1.amazonaws.com:5432/d19d1cqd47ej3e'#'mysql+pymysql://fab:fab@localhost:3306/fabtest'#os.environ.get('CLEARDB_DATABASE_URL').replace('mysql://','mysql+pymysql://')#'mysql+pymysql://test:test@localhost:3306/test'
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

