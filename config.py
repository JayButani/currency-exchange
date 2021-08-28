import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """Base configuration"""

    user = "postgres"
    password = "postgres"
    hostname = "localhost"
    port = 5432
    database = 'currency_converter'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('SQLALCHEMY_DATABASE_URL')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
class ProductionConfig(Config):
    """Production configuration"""


class DevelopmentConfig(Config):
    """Development configuration"""
    

class TestingConfig(Config):
    TESTING = True
    LOGIN_DISABLED = True