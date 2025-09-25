from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()  # ✅ Initialize CSRFProtect

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)  # ✅ Bind CSRF to app

    from app.routes.auth import auth_bp
    from app.routes.trades import trades_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(trades_bp)

    return app
