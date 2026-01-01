from flask import Blueprint

api_bp = Blueprint('api', __name__)

from . import routes
from .auth import auth_bp
api_bp.register_blueprint(auth_bp, url_prefix='/auth')

from app.extensions import jwt
from flask import jsonify

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Invalid token", "error": error}), 422

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"message": "Request does not contain an access token", "error": error}), 401
