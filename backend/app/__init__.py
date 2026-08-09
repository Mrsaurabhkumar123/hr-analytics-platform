"""
Application factory. Keeping construction here (rather than at import time)
makes the app testable and lets config be swapped per-environment.
"""
import logging
import os
from flask import Flask, jsonify

from app.config import config_by_name
from app.extensions import db, jwt, cors


def create_app(env_name: str = None) -> Flask:
    env_name = env_name or os.environ.get("FLASK_ENV", "production")
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(env_name, config_by_name["production"]))

    _configure_logging(app)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGIN"]}},
        supports_credentials=True,
    )

    _register_blueprints(app)
    _register_error_handlers(app)
    _register_jwt_callbacks(app)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "hr-analytics-backend"})

    return app


def _configure_logging(app: Flask) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))
    app.logger.handlers = [handler]
    app.logger.setLevel(logging.INFO if not app.config.get("DEBUG") else logging.DEBUG)


def _register_blueprints(app: Flask) -> None:
    from app.routes.auth import auth_bp
    from app.routes.employees import employees_bp
    from app.routes.departments import departments_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.attrition import attrition_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(employees_bp, url_prefix="/api/employees")
    app.register_blueprint(departments_bp, url_prefix="/api/departments")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(attrition_bp, url_prefix="/api/attrition")


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "not_found", "message": "Resource not found."}), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception("Unhandled server error")
        return jsonify({"error": "server_error", "message": "Something went wrong."}), 500

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "bad_request", "message": str(e)}), 400


def _register_jwt_callbacks(app: Flask) -> None:
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "token_expired", "message": "Session expired, please log in again."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "invalid_token", "message": "Invalid authentication token."}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return jsonify({"error": "unauthorized", "message": "Authentication required."}), 401
