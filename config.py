import os


class BaseConfig:
    """Base configuration"""
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PARENT_BASE_URL = os.environ.get("PARENT_BASE_URL")


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')


class StagingConfig(BaseConfig):
    """Staging configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class ProductionConfig(BaseConfig):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
