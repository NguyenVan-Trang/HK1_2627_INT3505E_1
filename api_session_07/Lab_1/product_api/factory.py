
from flask import Flask, app

from .config import DefaultConfig
from .extensions import db, migrate
from .api.errors import register_error_handlers
from .api.products import products_bp
from .api.orders import orders_bp
from product_api.api.health import health_bp


def create_app(config=None):
    app = Flask(__name__)

    app.config.from_object(config or DefaultConfig)
    
    db.init_app(app)
    migrate.init_app(app, db)

    register_error_handlers(app)
    
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(health_bp)
    
    return app
