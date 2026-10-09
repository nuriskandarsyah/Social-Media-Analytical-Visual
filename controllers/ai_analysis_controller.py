from flask import Blueprint, request, jsonify

from services.ai_analysis_service import AIAnalysisService


# =========================================================
# AI ANALYSIS BLUEPRINT
# =========================================================

ai_analysis_bp = Blueprint(
    "ai_analysis",
    __name__,
    url_prefix="/api/ai-analysis"
)


# =========================================================
# HELPER
# =========================================================

def _get_filters():
    """
    Ambil filter bulan dan tahun dari JSON request.

    Request yang diperbolehkan:
    {
        "month": 9,
        "year": 2026
    }

    Field kosong akan dianggap None.
    """
    data = request.get_json(
        silent=True
    ) or {}

    month = data.get(
        "month"
    )

    year = data.get(
        "year"
    )

    if month in (
        "",
        None
    ):
        month = None
    else:
        month = int(month)

    if year in (
        "",
        None
    ):
        year = None
    else:
        year = int(year)

    return (
        month,
        year
    )


def _analysis_response(
    result,
    message="Analisis AI berhasil"
):
    """
    Bentuk response standar yang dipakai frontend.
    """
    return jsonify({
        "success": True,
        "message": message,
        "data": result
    }), 200


# =========================================================
# UNIFIED AI ANALYSIS
# =========================================================
#
# POST /api/ai-analysis/
#
# Endpoint ini adalah endpoint utama halaman Analisis AI.
#
# Satu kali request menghasilkan:
# - total_content
# - cluster
# - cluster_summary
# - ai_insight
# - forecast
# - forecast_per_content
# - best_content_next_week
# - strategy
#
# Tidak perlu lagi frontend menggabungkan tiga endpoint.
# =========================================================

@ai_analysis_bp.route(
    "/",
    methods=["POST"]
)
def ai_analysis():

    try:

        month, year = (
            _get_filters()
        )

        result = (
            AIAnalysisService
            .analyze(
                month=month,
                year=year
            )
        )

        return _analysis_response(
            result,
            "Analisis AI berhasil"
        )

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        print(
            "AI ANALYSIS ERROR:",
            repr(e)
        )

        return jsonify({
            "success": False,
            "message":
                "Analisis AI gagal",
            "error":
                str(e)
        }), 500


# =========================================================
# CLUSTERING
# =========================================================
#
# Endpoint lama tetap dipertahankan agar halaman/fitur lain
# tidak rusak.
#
# POST /api/ai-analysis/clustering
# =========================================================

@ai_analysis_bp.route(
    "/clustering",
    methods=["POST"]
)
def clustering():

    try:

        month, year = (
            _get_filters()
        )

        result = (
            AIAnalysisService
            .analyze(
                month=month,
                year=year
            )
        )

        return jsonify({
            "success": True,
            "message":
                "Analisis clustering berhasil",
            "data": {
                "total_content":
                    result.get(
                        "total_content",
                        0
                    ),

                "cluster":
                    result.get(
                        "cluster",
                        {}
                    ),

                "cluster_summary":
                    result.get(
                        "cluster_summary",
                        []
                    )
            }
        }), 200

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        print(
            "CLUSTERING ERROR:",
            repr(e)
        )

        return jsonify({
            "success": False,
            "message":
                "Analisis clustering gagal",
            "error":
                str(e)
        }), 500


# =========================================================
# FORECAST
# =========================================================
#
# Endpoint lama tetap dipertahankan.
#
# POST /api/ai-analysis/forecast
# =========================================================

@ai_analysis_bp.route(
    "/forecast",
    methods=["POST"]
)
def forecast():

    try:

        month, year = (
            _get_filters()
        )

        result = (
            AIAnalysisService
            .analyze(
                month=month,
                year=year
            )
        )

        return jsonify({
            "success": True,
            "message":
                "Forecast berhasil",
            "data": {
                "forecast":
                    result.get(
                        "forecast",
                        []
                    ),

                "forecast_per_content":
                    result.get(
                        "forecast_per_content",
                        {}
                    ),

                "best_content_next_week":
                    result.get(
                        "best_content_next_week",
                        {}
                    )
            }
        }), 200

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        print(
            "FORECAST ERROR:",
            repr(e)
        )

        return jsonify({
            "success": False,
            "message":
                "Forecast gagal",
            "error":
                str(e)
        }), 500


# =========================================================
# RECOMMENDATIONS
# =========================================================
#
# Endpoint lama tetap dipertahankan.
#
# POST /api/ai-analysis/recommendations
# =========================================================

@ai_analysis_bp.route(
    "/recommendations",
    methods=["POST"]
)
def recommendations():

    try:

        month, year = (
            _get_filters()
        )

        result = (
            AIAnalysisService
            .analyze(
                month=month,
                year=year
            )
        )

        # Simpan hasil rekomendasi ke database.
        saved = (
            AIAnalysisService
            .save_recommendation(
                result.get(
                    "ai_insight",
                    {}
                ),
                result.get(
                    "strategy",
                    []
                )
            )
        )

        return jsonify({
            "success": True,
            "message":
                "Rekomendasi berhasil",
            "data": {
                "ai_insight":
                    result.get(
                        "ai_insight",
                        {}
                    ),

                "best_content_next_week":
                    result.get(
                        "best_content_next_week",
                        {}
                    ),

                "strategy":
                    result.get(
                        "strategy",
                        []
                    ),

                "saved":
                    saved
            }
        }), 200

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        print(
            "RECOMMENDATIONS ERROR:",
            repr(e)
        )

        return jsonify({
            "success": False,
            "message":
                "Rekomendasi gagal",
            "error":
                str(e)
        }), 500
