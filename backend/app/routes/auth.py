"""
Authentication routes: login, token refresh, current-user, logout, and
password change. Registration of new users is intentionally restricted to
HR Admin / Super Admin via a separate admin-only endpoint (not self-signup),
matching how enterprise HR systems are provisioned.
"""
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

from app.extensions import db
from app.models.user import User, Role
from app.utils.validators import is_valid_email, is_strong_password
from app.utils.decorators import roles_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not is_valid_email(email) or not password:
        return jsonify({"error": "invalid_input", "message": "Valid email and password are required."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid_credentials", "message": "Incorrect email or password."}), 401

    if not user.is_active:
        return jsonify({"error": "account_disabled", "message": "This account has been disabled."}), 403

    user.last_login_at = datetime.utcnow()
    db.session.commit()

    extra_claims = {"role": user.role, "full_name": user.full_name}
    access_token = create_access_token(identity=str(user.id), additional_claims=extra_claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=extra_claims)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict(),
    })


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    if not user or not user.is_active:
        return jsonify({"error": "invalid_user", "message": "User no longer active."}), 401

    extra_claims = {"role": user.role, "full_name": user.full_name}
    access_token = create_access_token(identity=str(user.id), additional_claims=extra_claims)
    return jsonify({"access_token": access_token})


@auth_bp.get("/me")
@jwt_required()
def me():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    if not user:
        return jsonify({"error": "not_found", "message": "User not found."}), 404
    return jsonify(user.to_dict())


@auth_bp.post("/change-password")
@jwt_required()
def change_password():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    payload = request.get_json(silent=True) or {}
    current_password = payload.get("current_password") or ""
    new_password = payload.get("new_password") or ""

    if not user or not user.check_password(current_password):
        return jsonify({"error": "invalid_credentials", "message": "Current password is incorrect."}), 401

    if not is_strong_password(new_password):
        return jsonify({
            "error": "weak_password",
            "message": "New password must be at least 8 characters and include a letter and a number.",
        }), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Password updated successfully."})


@auth_bp.post("/users")
@jwt_required()
@roles_required(Role.SUPER_ADMIN, Role.HR_ADMIN)
def create_user():
    """Admin-only provisioning of new platform users/roles."""
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    full_name = (payload.get("full_name") or "").strip()
    password = payload.get("password") or ""
    role = payload.get("role", Role.EMPLOYEE)

    if not is_valid_email(email) or not full_name:
        return jsonify({"error": "invalid_input", "message": "Valid email and full name are required."}), 400
    if not is_strong_password(password):
        return jsonify({
            "error": "weak_password",
            "message": "Password must be at least 8 characters and include a letter and a number.",
        }), 400
    if role not in Role.ALL:
        return jsonify({"error": "invalid_role", "message": f"Role must be one of {Role.ALL}."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "duplicate_email", "message": "A user with this email already exists."}), 409

    user = User(email=email, full_name=full_name, role=role, is_email_verified=False)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201
