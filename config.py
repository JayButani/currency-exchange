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
        os.environ.get('DATABASE_URL')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    is_prod = os.environ.get('IS_HEROKU', None)
    print('---------------------------------')
    print(is_prod)
class ProductionConfig(Config):
    """Production configuration"""


class DevelopmentConfig(Config):
    """Development configuration"""
    

class TestingConfig(Config):
    TESTING = True
    LOGIN_DISABLED = True