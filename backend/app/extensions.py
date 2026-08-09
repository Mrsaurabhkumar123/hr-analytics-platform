"""
Shared extension instances. Kept separate from app/__init__.py to avoid
circular imports between models, routes, and the app factory.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
