from flask import Blueprint, request, jsonify

from services.sync_log_service import (
    SyncLogService
)


sync_log_bp = Blueprint(
    "sync_log",
    __name__,
    url_prefix="/api/sync-log"
)


@sync_log_bp.route(
    "/",
    methods=["GET"]
)
def get_sync_logs():

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = request.args.get(
        "per_page",
        10,
        type=int
    )

    if page < 1:
        page = 1

    if per_page < 1:
        per_page = 10

    if per_page > 100:
        per_page = 100

    try:

        data = (
            SyncLogService
            .get_all(
                page=page,
                per_page=per_page
            )
        )

        return jsonify({
            "success": True,
            "message": (
                "Data SyncLog berhasil diambil"
            ),
            "data": data["items"],
            "pagination": data["pagination"]
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": (
                "Gagal mengambil data SyncLog"
            ),
            "error": str(e)
        }), 500


@sync_log_bp.route(
    "/<int:id_sync>",
    methods=["GET"]
)
def get_sync_log(id_sync):

    try:

        data = (
            SyncLogService
            .get_by_id(
                id_sync
            )
        )

        if not data:

            return jsonify({
                "success": False,
                "message": (
                    "SyncLog tidak ditemukan"
                )
            }), 404

        return jsonify({
            "success": True,
            "message": (
                "Detail SyncLog berhasil diambil"
            ),
            "data": data
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": (
                "Gagal mengambil detail SyncLog"
            ),
            "error": str(e)
        }), 500