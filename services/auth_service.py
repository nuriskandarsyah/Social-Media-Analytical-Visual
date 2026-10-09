from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token

from models import Users


class AuthService:

    @staticmethod
    def login(username, password):

        user = Users.query.filter_by(
            username=username
        ).first()

        if not user:
            return {
                "success": False,
                "message": "Username atau password salah"
            }

        if not check_password_hash(
            user.password,
            password
        ):
            return {
                "success": False,
                "message": "Username atau password salah"
            }

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "username": user.username,
                "role": user.role
            }
        )

        return {
            "success": True,
            "message": "Login berhasil",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        }