from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import config
from app.models import db

migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"]}})
    
    # Register blueprints
    from app.routes import auth, entries, user
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(entries.bp, url_prefix='/api/entries')
    app.register_blueprint(user.bp, url_prefix='/api/user')
    
    # Create upload directory
    import os
    upload_path = os.path.join(app.root_path, '..', app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_path, exist_ok=True)
    
    return app