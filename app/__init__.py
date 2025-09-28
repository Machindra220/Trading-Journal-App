from flask import Flask, render_template
from config import Config
from flask_login import current_user
from app.extensions import db, login_manager, csrf, cache
from app.models import Resource
from dotenv import load_dotenv
load_dotenv()

# app.config.from_object(Config)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    csrf.init_app(app)
    cache.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.trades import trades_bp
    from app.routes.stats import stats_bp
    from app.routes.export import export_bp
    from app.routes.resources import resources_bp
    from app.routes.notes import notes_bp
    from app.routes.calendar import calendar_bp
    from app.routes.watchlist import watchlist_bp

    app.register_blueprint(calendar_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(trades_bp)
    app.register_blueprint(stats_bp, url_prefix='/stats')
    app.register_blueprint(export_bp)
    app.register_blueprint(resources_bp, url_prefix='/resources')    
    app.register_blueprint(notes_bp)
    app.register_blueprint(watchlist_bp)

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.context_processor
    def inject_pinned_resources():
        if login_manager._login_disabled or not hasattr(app, 'login_manager'):
            return dict(pinned_resources=[])
        if current_user.is_authenticated:
            pinned = Resource.query.filter_by(user_id=current_user.id, pinned=True).order_by(Resource.title).all()
            return dict(pinned_resources=pinned)
        return dict(pinned_resources=[])

    return app
