from flask import Blueprint, request, jsonify

from services.llm_chat_service import LLMChatService


llm_chat_bp = Blueprint(
    "llm_chat",
    __name__,
    url_prefix="/api/llm-chat"
)


@llm_chat_bp.route("/", methods=["POST"])
def chat():

    data = request.get_json() or {}

    message = data.get("message")
    instagram_user_id = data.get(
        "instagram_user_id"
    )

    # =====================================================
    # VALIDASI MESSAGE
    # =====================================================

    if (
        not message
        or not str(message).strip()
    ):

        return jsonify({

            "success": False,

            "message":
                "Pesan wajib diisi"

        }), 400


    try:

        # =================================================
        # GENERATE CHAT
        # =================================================

        result = LLMChatService.chat(

            message=
                str(message).strip(),

            instagram_user_id=
                instagram_user_id

        )


        # =================================================
        # SUCCESS
        # =================================================

        return jsonify({

            "success": True,

            "message":
                "LLM Chat berhasil",

            "data":
                result

        }), 200


    except Exception as e:

        error_text = str(e)

        print(
            "LLM CHAT ERROR:",
            repr(e)
        )


        # =================================================
        # GEMINI 503
        # =================================================

        if (
            "503" in error_text
            or "UNAVAILABLE" in error_text.upper()
            or "SERVICE_UNAVAILABLE"
            in error_text.upper()
        ):

            return jsonify({

                "success": False,

                "message":
                    "Layanan AI sedang sibuk. "
                    "Silakan coba kembali beberapa saat lagi.",

                "error":
                    error_text,

                "retryable":
                    True

            }), 503


        # =================================================
        # GEMINI 429
        # =================================================

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED"
            in error_text.upper()
        ):

            return jsonify({

                "success": False,

                "message":
                    "Batas penggunaan layanan AI "
                    "sedang tercapai. Silakan coba "
                    "kembali beberapa saat lagi.",

                "error":
                    error_text,

                "retryable":
                    True

            }), 429


        # =================================================
        # ERROR LAIN
        # =================================================

        return jsonify({

            "success": False,

            "message":
                "LLM Chat gagal",

            "error":
                error_text,

            "retryable":
                False

        }), 500