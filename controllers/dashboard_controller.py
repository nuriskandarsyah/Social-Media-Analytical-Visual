from flask import Blueprint, request, jsonify

from services.dashboard_service import DashboardService
from utils.auth import jwt_required_role


dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/api/dashboard"
)


@dashboard_bp.route("/", methods=["GET"])
@jwt_required_role("admin", "manager")
def get_dashboard():

    month = request.args.get(
        "month",
        type=int
    )

    year = request.args.get(
        "year",
        type=int
    )

    try:

        data = DashboardService.get_dashboard(
            month=month,
            year=year
        )

        return jsonify({
            "success": True,
            "message": "Data dashboard berhasil diambil",
            "data": data
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": "Gagal mengambil data dashboard",
            "error": str(e)
        }), 500