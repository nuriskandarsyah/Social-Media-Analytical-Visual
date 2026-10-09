from flask import (
    Blueprint,
    jsonify,
    request,
    render_template_string
)

from services.meta_connection_service import (
    MetaConnectionService
)

from utils.auth import jwt_required_role


meta_connection_bp = Blueprint(
    "meta_connection",
    __name__,
    url_prefix="/api/meta"
)


# =========================================================
# CONNECT META / INSTAGRAM
# =========================================================

@meta_connection_bp.route(
    "/connect",
    methods=["GET"]
)
@jwt_required_role("admin")
def connect_meta():

    try:

        result = (
            MetaConnectionService
            .connect_meta_account()
        )

        return jsonify({
            "success": True,
            "message": (
                "URL login Instagram berhasil dibuat"
            ),
            "data": result
        }), 200

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "success": False,
            "message": (
                "Gagal membuat koneksi Instagram"
            ),
            "error": str(e)
        }), 500


# =========================================================
# OAUTH CALLBACK
# =========================================================

@meta_connection_bp.route(
    "/callback",
    methods=["GET"]
)
def meta_callback():

    error = request.args.get("error")

    error_reason = request.args.get(
        "error_reason"
    )

    error_description = request.args.get(
        "error_description"
    )

    # =====================================================
    # OAUTH ERROR
    # =====================================================

    if error:

        message = (
            error_description
            or error_reason
            or error
        )

        return render_template_string(
            """
            <!DOCTYPE html>

            <html>
            <head>
                <meta charset="UTF-8">
                <title>MAVis</title>
            </head>

            <body>

                <div style="
                    font-family: Arial;
                    text-align: center;
                    margin-top: 100px;
                ">

                    <h2>
                        Koneksi Instagram gagal
                    </h2>

                    <p>
                        {{ message }}
                    </p>

                    <p>
                        Jendela akan ditutup...
                    </p>

                </div>

                <script>

                    const payload = {
                        type:
                            "INSTAGRAM_OAUTH_ERROR",

                        message:
                            {{ message | tojson }}
                    };

                    localStorage.setItem(
                        "mavis_instagram_oauth",
                        JSON.stringify(payload)
                    );

                    setTimeout(
                        function () {
                            window.close();
                        },
                        1000
                    );

                </script>

            </body>
            </html>
            """,
            message=message
        )


    # =====================================================
    # GET CODE
    # =====================================================

    code = request.args.get(
        "code"
    )

    state = request.args.get(
        "state"
    )

    if not code:

        message = (
            "Authorization code "
            "tidak ditemukan."
        )

        return render_template_string(
            """
            <!DOCTYPE html>

            <html>
            <head>
                <meta charset="UTF-8">
                <title>MAVis</title>
            </head>

            <body>

                <div style="
                    font-family: Arial;
                    text-align: center;
                    margin-top: 100px;
                ">

                    <h2>
                        Koneksi Instagram gagal
                    </h2>

                    <p>
                        {{ message }}
                    </p>

                </div>

                <script>

                    const payload = {
                        type:
                            "INSTAGRAM_OAUTH_ERROR",

                        message:
                            {{ message | tojson }}
                    };

                    localStorage.setItem(
                        "mavis_instagram_oauth",
                        JSON.stringify(payload)
                    );

                    setTimeout(
                        function () {
                            window.close();
                        },
                        1000
                    );

                </script>

            </body>
            </html>
            """,
            message=message
        )


    # =====================================================
    # HANDLE CALLBACK
    # =====================================================

    try:

        result = (
            MetaConnectionService
            .handle_callback(
                code=code,
                state=state
            )
        )

        # =================================================
        # SUCCESS
        # =================================================

        return render_template_string(
            """
            <!DOCTYPE html>

            <html>

            <head>
                <meta charset="UTF-8">

                <title>
                    MAVis - Instagram
                </title>
            </head>

            <body>

                <div style="
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin-top: 100px;
                ">

                    <div style="
                        width: 64px;
                        height: 64px;
                        border-radius: 50%;
                        background: #22c55e;
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 20px;
                        font-size: 34px;
                    ">
                        ✓
                    </div>

                    <h2>
                        Instagram berhasil terhubung
                    </h2>

                    <p style="
                        color: #64748b;
                    ">
                        Mengembalikan ke MAVis...
                    </p>

                </div>


                <script>

                    const payload = {
                        type:
                            "INSTAGRAM_OAUTH_SUCCESS",

                        data:
                            {{ result | tojson }}
                    };


                    // =====================================
                    // SIMPAN HASIL OAUTH
                    // =====================================

                    localStorage.setItem(
                        "mavis_instagram_oauth",
                        JSON.stringify(payload)
                    );


                    // =====================================
                    // TUTUP POPUP
                    // =====================================

                    setTimeout(
                        function () {

                            window.close();

                        },
                        1000
                    );

                </script>

            </body>

            </html>
            """,
            result=result
        )


    except ValueError as e:

        message = str(e)

        return render_template_string(
            """
            <!DOCTYPE html>

            <html>

            <head>
                <meta charset="UTF-8">
                <title>MAVis</title>
            </head>

            <body>

                <div style="
                    font-family: Arial;
                    text-align: center;
                    margin-top: 100px;
                ">

                    <h2>
                        Koneksi Instagram gagal
                    </h2>

                    <p>
                        {{ message }}
                    </p>

                </div>


                <script>

                    const payload = {

                        type:
                            "INSTAGRAM_OAUTH_ERROR",

                        message:
                            {{ message | tojson }}

                    };


                    localStorage.setItem(
                        "mavis_instagram_oauth",
                        JSON.stringify(payload)
                    );


                    setTimeout(
                        function () {

                            window.close();

                        },
                        1500
                    );

                </script>

            </body>

            </html>
            """,
            message=message
        )


    except Exception as e:

        message = str(e)

        return render_template_string(
            """
            <!DOCTYPE html>

            <html>

            <head>
                <meta charset="UTF-8">
                <title>MAVis</title>
            </head>

            <body>

                <div style="
                    font-family: Arial;
                    text-align: center;
                    margin-top: 100px;
                ">

                    <h2>
                        Terjadi kesalahan
                    </h2>

                    <p>
                        {{ message }}
                    </p>

                </div>


                <script>

                    const payload = {

                        type:
                            "INSTAGRAM_OAUTH_ERROR",

                        message:
                            {{ message | tojson }}

                    };


                    localStorage.setItem(
                        "mavis_instagram_oauth",
                        JSON.stringify(payload)
                    );


                    setTimeout(
                        function () {

                            window.close();

                        },
                        1500
                    );

                </script>

            </body>

            </html>
            """,
            message=message
        )


# =========================================================
# STATUS
# =========================================================

@meta_connection_bp.route(
    "/status",
    methods=["GET"]
)
@jwt_required_role(
    "admin",
    "manager"
)
def get_connection_status():

    try:

        result = (
            MetaConnectionService
            .get_status()
        )

        return jsonify({
            "success": True,
            "message": (
                "Status koneksi Instagram "
                "berhasil diambil"
            ),
            "data": result
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": (
                "Gagal mengambil status "
                "koneksi Instagram"
            ),
            "error": str(e)
        }), 500


# =========================================================
# SYNCHRONIZE
# =========================================================

@meta_connection_bp.route(
    "/synchronize",
    methods=["POST"]
)
@jwt_required_role("admin")
def synchronize_data():

    try:

        result = (
            MetaConnectionService
            .synchronize()
        )

        return jsonify({
            "success": True,
            "message": (
                "Sinkronisasi Instagram "
                "berhasil"
            ),
            "data": result
        }), 200

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "success": False,
            "message": (
                "Sinkronisasi Instagram gagal"
            ),
            "error": str(e)
        }), 500