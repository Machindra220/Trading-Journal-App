from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_caching import Cache  # ✅ Add caching
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})  # ✅ In-memory cache

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)
    cache.init_app(app)  # ✅ Bind cache to app

    from app.routes.auth import auth_bp     # ✅ Import your auth blueprint
    from app.routes.trades import trades_bp # ✅ Import your trades blueprint
    from app.routes.stats import stats_bp   # ✅ Import your stats blueprint

    app.register_blueprint(auth_bp)         # Purpose of blueprint - Login, register, logout
    app.register_blueprint(trades_bp)       # Purpose of this blueprint - Trade lifecycle routes
    app.register_blueprint(stats_bp, url_prefix='/stats')   # Purpose of this blueprint - stats

    from app.routes.export import export_bp
    app.register_blueprint(export_bp)


    return app
