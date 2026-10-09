from flask import Blueprint, jsonify, request

from services.meta_insight_service import MetaInsightService
from utils.auth import jwt_required_role


meta_insight_bp = Blueprint(
    "meta_insight",
    __name__,
    url_prefix="/api/meta-insight"
)


@meta_insight_bp.route("/", methods=["GET"])
@jwt_required_role("admin", "manager")
def get_insight():

    try:

        month = request.args.get(
            "month",
            type=int
        )

        year = request.args.get(
            "year",
            type=int
        )

        result = MetaInsightService.generate_insight(
            month=month,
            year=year
        )

        return jsonify({
            "success": True,
            "message": "Meta insight berhasil diambil",
            "data": result
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Gagal mengambil meta insight",
            "error": str(e)
        }), 500