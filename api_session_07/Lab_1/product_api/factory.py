
from flask import Flask

from .config import DefaultConfig
from .extensions import db, migrate
from .api.errors import register_error_handlers
from .api.products import products_bp


def create_app(config=None):
    app = Flask(__name__)

    app.config.from_object(config or DefaultConfig)
    
    db.init_app(app)
    migrate.init_app(app, db)

    register_error_handlers(app)
    
    app.register_blueprint(products_bp)
    
    return app
