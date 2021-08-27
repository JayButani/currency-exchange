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
        "postgres://risevocfkzegwg:a231586eda5f1d6ed64fd6332baf1e0ecae0c0aadf17047f1b429dd3734538b2@ec2-18-209-153-180.compute-1.amazonaws.com:5432/dccnrnppmjka24"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    """Production configuration"""


class DevelopmentConfig(Config):
    """Development configuration"""
    

class TestingConfig(Config):
    TESTING = True
    LOGIN_DISABLED = True