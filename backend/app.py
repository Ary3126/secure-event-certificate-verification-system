from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import text
from .config import config
from .models import db
from .auth import auth_bp
from .routes import main_bp
from .verification import verify_bp

def _ensure_sqlite_schema():
    """
    Lightweight schema guard for existing SQLite files.
    db.create_all() creates missing tables, but it won't rename columns.
    This app expects specific columns for the Admin/Student split.
    """
    engine = db.engine
    if engine.dialect.name != "sqlite":
        return

    # If an old database exists (from before the admin/student split),
    # the `templates` and `certificates` tables won't have the expected columns.
    def has_column(table: str, column: str) -> bool:
        cols = {row[1] for row in db.session.execute(text(f"PRAGMA table_info({table})")).all()}
        return column in cols

    if not has_column("templates", "admin_id") or not has_column("certificates", "student_id"):
        raise RuntimeError(
            "Database schema mismatch. Delete `sgp.db` and run `init_db.py` to recreate tables "
            "for the Admin/Student split."
        )

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
    
    # Load configuration
    cfg = config.get(config_name)
    app.config.from_object(cfg)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(verify_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
        _ensure_sqlite_schema()
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)
