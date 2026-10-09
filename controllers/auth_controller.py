from flask import Blueprint, request, jsonify

from flask_jwt_extended import get_jwt_identity, get_jwt

from services.auth_service import AuthService
from utils.auth import jwt_required_role


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Data login tidak ditemukan"
        }), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Username dan password wajib diisi"
        }), 400

    result = AuthService.login(
        username=username,
        password=password
    )

    if not result["success"]:
        return jsonify(result), 401

    return jsonify(result), 200


@auth_bp.route("/profile", methods=["GET"])
@jwt_required_role("admin", "manager")
def profile():

    user_id = get_jwt_identity()
    claims = get_jwt()

    return jsonify({
        "success": True,
        "user": {
            "id": user_id,
            "username": claims.get("username"),
            "role": claims.get("role")
        }
    }), 200