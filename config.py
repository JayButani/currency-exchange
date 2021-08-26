import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """Base configuration"""

    user = "postgres"
    password = "postgres"
    hostname = "localhost"
    port = 5432
    database = 'currency_converter'
    SECRET_KEY = '3FVpR2VRHl-8LVggkfDuQ'
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{user}:{password}@{hostname}:{port}/{database}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    """Production configuration"""


class DevelopmentConfig(Config):
    """Development configuration"""
    

class TestingConfig(Config):
    TESTING = True