import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '62202e6a2a0f0ec39b04d89639fb8d9fc57f223aeae5138ae956d7a838a2f592'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@localhost/portfolio_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    REMEMBER_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
