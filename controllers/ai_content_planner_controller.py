from flask import (
    Blueprint,
    request,
    jsonify
)

from services.ai_content_planner_service import (
    AIContentPlannerService
)


# =========================================================
# BLUEPRINT
# =========================================================

ai_content_planner_bp = Blueprint(
    "ai_content_planner",
    __name__,
    url_prefix="/api/ai-content-planner"
)


# =========================================================
# HELPER - ACTIVE INSTAGRAM ACCOUNT
# =========================================================

def get_instagram_user_id():

    # -----------------------------------------------------
    # GET ?instagram_user_id=...
    # -----------------------------------------------------

    value = request.args.get(
        "instagram_user_id"
    )

    if value:

        return str(
            value
        ).strip()


    # -----------------------------------------------------
    # POST JSON
    # -----------------------------------------------------

    payload = (
        request.get_json(
            silent=True
        )
        or {}
    )

    value = payload.get(
        "instagram_user_id"
    )

    if value:

        return str(
            value
        ).strip()


    return None


# =========================================================
# GET CONTENT PLANNER
# =========================================================

@ai_content_planner_bp.route(
    "/",
    methods=["GET"]
)
def get_content_recommendations():

    try:

        instagram_user_id = (
            get_instagram_user_id()
        )


        # -------------------------------------------------
        # Untuk saat ini ContentRecommendations belum
        # mempunyai kolom instagram_user_id. Karena itu
        # service get_all() belum difilter berdasarkan akun.
        # Parameter tetap dibaca agar endpoint siap ketika
        # ownership akun ditambahkan pada model.
        # -------------------------------------------------

        data = (
            AIContentPlannerService
            .get_all()
        )


        return jsonify({

            "success":
                True,

            "message":
                (
                    "Data Content Recommendations "
                    "berhasil diambil"
                ),

            "instagram_user_id":
                instagram_user_id,

            "data":
                data

        }), 200


    except Exception as e:

        print("")
        print(
            "============================================"
        )
        print(
            "AI CONTENT PLANNER GET ERROR"
        )
        print(
            "============================================"
        )
        print(
            "ERROR TYPE:",
            type(e).__name__
        )
        print(
            "ERROR:",
            str(e)
        )
        print(
            "============================================"
        )
        print("")


        return jsonify({

            "success":
                False,

            "message":
                (
                    "Gagal mengambil Content "
                    "Recommendations"
                ),

            "error":
                str(e)

        }), 500


# =========================================================
# GENERATE CONTENT PLAN
# =========================================================

@ai_content_planner_bp.route(
    "/generate",
    methods=["POST"]
)
def generate_content_plan():

    # -----------------------------------------------------
    # REQUEST DATA
    # -----------------------------------------------------

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    number_of_days = data.get(
        "number_of_days",
        30
    )


    # -----------------------------------------------------
    # ACTIVE INSTAGRAM USER ID
    #
    # INI YANG SEBELUMNYA HILANG sehingga muncul:
    # "instagram_user_id is not defined"
    # -----------------------------------------------------

    instagram_user_id = (
        data.get(
            "instagram_user_id"
        )
        or
        request.args.get(
            "instagram_user_id"
        )
    )


    if instagram_user_id:

        instagram_user_id = str(
            instagram_user_id
        ).strip()


    # -----------------------------------------------------
    # VALIDATE ACCOUNT ID
    # -----------------------------------------------------

    if not instagram_user_id:

        return jsonify({

            "success":
                False,

            "message":
                (
                    "Instagram User ID akun aktif "
                    "belum tersedia."
                )

        }), 400


    # -----------------------------------------------------
    # GENERATE
    # -----------------------------------------------------

    try:

        number_of_days = int(
            number_of_days
        )


        if number_of_days <= 0:

            number_of_days = 30


        if number_of_days > 30:

            number_of_days = 30


        print("")
        print(
            "============================================"
        )
        print(
            "GENERATE AI CONTENT PLANNER"
        )
        print(
            "============================================"
        )
        print(
            "INSTAGRAM USER ID:",
            instagram_user_id
        )
        print(
            "NUMBER OF DAYS:",
            number_of_days
        )
        print(
            "============================================"
        )


        result = (
            AIContentPlannerService
            .generate_plan(

                number_of_days=
                    number_of_days,

                instagram_user_id=
                    instagram_user_id

            )
        )


        return jsonify({

            "success":
                True,

            "message":
                (
                    "Content Planner berhasil "
                    "dibuat"
                ),

            "data":
                result

        }), 200


    except ValueError as e:

        print(
            "AI CONTENT PLANNER VALUE ERROR:",
            str(e)
        )


        return jsonify({

            "success":
                False,

            "message":
                str(e)

        }), 400


    except Exception as e:

        import traceback


        print("")
        print(
            "============================================"
        )
        print(
            "AI CONTENT PLANNER GENERATE ERROR"
        )
        print(
            "============================================"
        )
        print(
            "ERROR TYPE:",
            type(e).__name__
        )
        print(
            "ERROR:",
            str(e)
        )
        print(
            "TRACEBACK:"
        )

        traceback.print_exc()

        print(
            "============================================"
        )
        print("")


        return jsonify({

            "success":
                False,

            "message":
                "Gagal membuat Content Planner",

            "error":
                (
                    f"{type(e).__name__}: "
                    f"{str(e)}"
                )

        }), 500


# =========================================================
# GET DETAIL
# =========================================================

@ai_content_planner_bp.route(
    "/<int:id_cr>",
    methods=["GET"]
)
def get_content_recommendation(
    id_cr
):

    try:

        data = (
            AIContentPlannerService
            .get_by_id(
                id_cr
            )
        )


        if not data:

            return jsonify({

                "success":
                    False,

                "message":
                    (
                        "Content Recommendation "
                        "tidak ditemukan"
                    )

            }), 404


        return jsonify({

            "success":
                True,

            "message":
                (
                    "Detail Content Recommendation "
                    "berhasil diambil"
                ),

            "data":
                data

        }), 200


    except Exception as e:

        print(
            "AI CONTENT PLANNER DETAIL ERROR:",
            repr(e)
        )


        return jsonify({

            "success":
                False,

            "message":
                (
                    "Gagal mengambil detail "
                    "Content Recommendation"
                ),

            "error":
                str(e)

        }), 500
