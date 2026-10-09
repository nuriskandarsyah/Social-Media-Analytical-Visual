from flask import (
    Blueprint,
    jsonify,
    request
)

from flask_jwt_extended import (
    get_jwt
)

from services.facebook_service import (
    FacebookService
)

from utils.auth import (
    jwt_required_role
)


facebook_bp = Blueprint(

    "facebook",

    __name__,

    url_prefix="/api/facebook"

)


# =====================================================
# STATUS
# =====================================================

@facebook_bp.route(
    "/status",
    methods=["GET"]
)
@jwt_required_role(
    "admin",
    "manager"
)
def get_facebook_status():

    try:

        claims = get_jwt()

        mavis_user_id = (
            claims.get(
                "sub"
            )
        )

        if mavis_user_id is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "User MAVis tidak ditemukan."

            }), 401

        result = (
            FacebookService
            .get_status(
                int(
                    mavis_user_id
                )
            )
        )

        return jsonify({

            "success":
                True,

            "message":
                "Status Facebook berhasil diambil",

            "data":
                result

        }), 200

    except Exception as e:

        return jsonify({

            "success":
                False,

            "message":
                "Gagal mengambil status Facebook",

            "error":
                str(e)

        }), 500


# =====================================================
# PAGES
# =====================================================

@facebook_bp.route(
    "/pages",
    methods=["GET"]
)
@jwt_required_role(
    "admin",
    "manager"
)
def get_facebook_pages():

    try:

        claims = get_jwt()

        mavis_user_id = (
            claims.get(
                "sub"
            )
        )

        if mavis_user_id is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "User MAVis tidak ditemukan."

            }), 401

        pages = (

            FacebookService
            .get_pages_from_database(

                int(
                    mavis_user_id
                )

            )

        )

        return jsonify({

            "success":
                True,

            "message":
                "Daftar Facebook Page berhasil diambil",

            "data":
                pages

        }), 200

    except Exception as e:

        return jsonify({

            "success":
                False,

            "message":
                "Gagal mengambil Facebook Page",

            "error":
                str(e)

        }), 500


# =====================================================
# SELECT PAGE
# =====================================================

@facebook_bp.route(
    "/select-page",
    methods=["POST"]
)
@jwt_required_role(
    "admin"
)
def select_facebook_page():

    try:

        body = (

            request.get_json(
                silent=True
            )

            or {}

        )

        page_id = str(

            body.get(
                "page_id"
            )

            or ""

        ).strip()

        if not page_id:

            return jsonify({

                "success":
                    False,

                "message":
                    "page_id wajib diisi"

            }), 400

        claims = get_jwt()

        mavis_user_id = (
            claims.get(
                "sub"
            )
        )

        if mavis_user_id is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "User MAVis tidak ditemukan."

            }), 401

        page = (

            FacebookService
            .select_page(

                int(
                    mavis_user_id
                ),

                page_id

            )

        )

        if page is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "Facebook Page tidak ditemukan"

            }), 404

        return jsonify({

            "success":
                True,

            "message":
                "Facebook Page berhasil dipilih",

            "data":
                page

        }), 200

    except Exception as e:

        return jsonify({

            "success":
                False,

            "message":
                "Gagal memilih Facebook Page",

            "error":
                str(e)

        }), 500


# =====================================================
# LIVE INSIGHTS + SAVE DATABASE
# =====================================================

@facebook_bp.route(
    "/insights",
    methods=["GET"]
)
@jwt_required_role(
    "admin",
    "manager"
)
def get_facebook_insights():

    try:

        claims = get_jwt()

        mavis_user_id = (
            claims.get(
                "sub"
            )
        )

        if mavis_user_id is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "User MAVis tidak ditemukan."

            }), 401

        metric = (

            request.args.get(
                "metric"
            )

            or ""

        ).strip()

        if not metric:

            return jsonify({

                "success":
                    False,

                "message":
                    (
                        "Parameter metric wajib diisi."
                    )

            }), 400

        page_id = (

            request.args.get(
                "page_id"
            )

            or None

        )

        period = (

            request.args.get(
                "period"
            )

            or None

        )

        since = (

            request.args.get(
                "since"
            )

            or None

        )

        until = (

            request.args.get(
                "until"
            )

            or None

        )

        result = (

            FacebookService
            .sync_insights(

                mavis_user_id=
                    int(
                        mavis_user_id
                    ),

                metric=
                    metric,

                page_id=
                    page_id,

                period=
                    period,

                since=
                    since,

                until=
                    until

            )

        )

        return jsonify({

            "success":
                True,

            "message":
                (
                    "Facebook Page Insights "
                    "berhasil diambil dan disimpan"
                ),

            "data":
                result

        }), 200

    except ValueError as e:

        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 400

    except Exception as e:

        return jsonify({

            "success":
                False,

            "message":
                "Gagal mengambil Facebook Insights",

            "error":
                str(e)

        }), 500


# =====================================================
# STORED INSIGHTS
# =====================================================

@facebook_bp.route(
    "/insights/history",
    methods=["GET"]
)
@jwt_required_role(
    "admin",
    "manager"
)
def get_facebook_insight_history():

    try:

        claims = get_jwt()

        mavis_user_id = (
            claims.get(
                "sub"
            )
        )

        if mavis_user_id is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "User MAVis tidak ditemukan."

            }), 401

        page_id = (
            request.args.get(
                "page_id"
            )
        )

        metric_name = (
            request.args.get(
                "metric"
            )
        )

        period = (
            request.args.get(
                "period"
            )
        )

        result = (

            FacebookService
            .get_stored_insights(

                mavis_user_id=
                    int(
                        mavis_user_id
                    ),

                page_id=
                    page_id,

                metric_name=
                    metric_name,

                period=
                    period

            )

        )

        return jsonify({

            "success":
                True,

            "message":
                (
                    "Riwayat Facebook Insights "
                    "berhasil diambil"
                ),

            "data":
                result

        }), 200

    except Exception as e:

        return jsonify({

            "success":
                False,

            "message":
                "Gagal mengambil riwayat Facebook Insights",

            "error":
                str(e)

        }), 500


# =====================================================
# CONTENT
# =====================================================

@facebook_bp.route(
    "/contents",
    methods=["GET"]
)
@jwt_required_role(
    "admin",
    "manager"
)
def get_facebook_contents():

    try:

        claims = get_jwt()

        mavis_user_id = (
            claims.get(
                "sub"
            )
        )

        if mavis_user_id is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "User MAVis tidak ditemukan."

            }), 401

        page_id = (
            request.args.get(
                "page_id"
            )
        )

        limit = request.args.get(
            "limit",
            default=25,
            type=int
        )

        limit = max(
            1,
            min(
                limit,
                100
            )
        )

        result = (

            FacebookService
            .sync_contents(

                mavis_user_id=
                    int(
                        mavis_user_id
                    ),

                page_id=
                    page_id,

                limit=
                    limit

            )

        )

        return jsonify({

            "success":
                True,

            "message":
                (
                    "Facebook Content "
                    "berhasil diambil dan disimpan"
                ),

            "data":
                result

        }), 200

    except ValueError as e:

        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 400

    except Exception as e:

        return jsonify({

            "success":
                False,

            "message":
                "Gagal mengambil Facebook Content",

            "error":
                str(e)

        }), 500


# =====================================================
# STORED CONTENT HISTORY
# =====================================================

@facebook_bp.route(
    "/contents/history",
    methods=["GET"]
)
@jwt_required_role(
    "admin",
    "manager"
)
def get_facebook_content_history():

    try:

        claims = get_jwt()

        mavis_user_id = (
            claims.get(
                "sub"
            )
        )

        if mavis_user_id is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "User MAVis tidak ditemukan."

            }), 401

        page_id = (
            request.args.get(
                "page_id"
            )
        )

        result = (

            FacebookService
            .get_stored_contents(

                mavis_user_id=
                    int(
                        mavis_user_id
                    ),

                page_id=
                    page_id

            )

        )

        return jsonify({

            "success":
                True,

            "message":
                (
                    "Riwayat Facebook Content "
                    "berhasil diambil"
                ),

            "data":
                result

        }), 200

    except Exception as e:

        return jsonify({

            "success":
                False,

            "message":
                "Gagal mengambil riwayat Facebook Content",

            "error":
                str(e)

        }), 500


# =====================================================
# SYNC ALL
# =====================================================

@facebook_bp.route(
    "/sync",
    methods=["POST"]
)
@jwt_required_role(
    "admin"
)
def sync_facebook():

    try:

        claims = get_jwt()

        mavis_user_id = (
            claims.get(
                "sub"
            )
        )

        if mavis_user_id is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "User MAVis tidak ditemukan."

            }), 401

        body = (

            request.get_json(
                silent=True
            )

            or {}

        )

        page_id = (
            body.get(
                "page_id"
            )
        )

        metric = (
            body.get(
                "metric"
            )

            or
            (
                "page_post_engagements,"
                "page_views_total,"
                "page_media_view"
            )

        )

        period = (

            body.get(
                "period"
            )

            or
            "days_28"

        )

        limit = body.get(
            "limit",
            25
        )

        insights_result = (

            FacebookService
            .sync_insights(

                mavis_user_id=
                    int(
                        mavis_user_id
                    ),

                metric=
                    metric,

                page_id=
                    page_id,

                period=
                    period

            )

        )

        contents_result = (

            FacebookService
            .sync_contents(

                mavis_user_id=
                    int(
                        mavis_user_id
                    ),

                page_id=
                    page_id,

                limit=
                    limit

            )

        )

        return jsonify({

            "success":
                True,

            "message":
                "Sinkronisasi Facebook berhasil",

            "data": {

                "insights":
                    insights_result,

                "contents":
                    contents_result

            }

        }), 200

    except ValueError as e:

        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 400

    except Exception as e:

        return jsonify({

            "success":
                False,

            "message":
                "Sinkronisasi Facebook gagal",

            "error":
                str(e)

        }), 500