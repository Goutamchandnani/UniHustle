from flask import Flask
from config import config
from app.extensions import db, migrate, celery
from app.celery_utils import init_celery

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    init_celery(app, celery)
    
    from app.extensions import jwt
    jwt.init_app(app)
    
    from flask_cors import CORS
    CORS(app)
    
    # Register Commands
    from .commands import scrape_reed_command
    app.cli.add_command(scrape_reed_command)

    # Register Blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')

    @app.route('/')
    def index():
        return "Smart Student Job Agent Backend Running!"

    return app
