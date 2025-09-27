from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_caching import Cache

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
