from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def jwt_required_role(*allowed_roles):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            try:
                verify_jwt_in_request()

                claims = get_jwt()
                role = claims.get("role")

                if role not in allowed_roles:
                    return jsonify({
                        "success": False,
                        "message": "Anda tidak memiliki akses"
                    }), 403

                return function(*args, **kwargs)

            except Exception:
                return jsonify({
                    "success": False,
                    "message": "Token tidak valid atau belum login"
                }), 401

        return wrapper

    return decorator