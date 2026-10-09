import os
import secrets
import hashlib
import hmac
from urllib.parse import urlencode
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()

from flask import (
    Flask,
    session,
    jsonify,
    request,
    render_template_string
)

from flask_cors import CORS
from sqlalchemy import text

from extensions import (
    db,
    jwt
)

from config import Config

from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt
)

from functools import wraps


# =========================================================
# JWT ROLE HELPER
# =========================================================

def jwt_required_role(*allowed_roles):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if request.method == "OPTIONS":
                return "", 204

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

            except Exception as e:

                print(
                    "JWT ERROR:",
                    str(e)
                )

                return jsonify({
                    "success": False,
                    "message": (
                        "Token tidak valid "
                        "atau belum login"
                    )
                }), 401

        return wrapper

    return decorator


# =========================================================
# META CONFIG
# =========================================================

META_APP_ID = os.getenv(
    "META_APP_ID"
)

META_APP_SECRET = os.getenv(
    "META_APP_SECRET"
)

META_REDIRECT_URI = os.getenv(
    "META_REDIRECT_URI"
)

META_OAUTH_URL = (
    os.getenv(
        "META_OAUTH_URL"
    )
    or
    "https://www.instagram.com/oauth/authorize"
)

META_TOKEN_URL = (
    os.getenv(
        "META_TOKEN_URL"
    )
    or
    "https://api.instagram.com/oauth/access_token"
)

META_TOKEN_EXCHANGE_URL = (
    "https://graph.instagram.com/access_token"
)

META_GRAPH_URL = (
    "https://graph.instagram.com"
)


# =========================================================
# INSTAGRAM PERMISSIONS
# =========================================================

META_SCOPES = (
    "instagram_business_basic,"
    "instagram_business_manage_insights"
)


# =========================================================
# FACEBOOK LOGIN FOR BUSINESS
# =========================================================

# IMPORTANT:
# FB_APP_ID harus merupakan App ID Meta yang memiliki
# Facebook Login for Business Configuration ID di bawah.
# Jangan mengganti META_APP_ID Instagram.

FB_APP_ID = os.getenv("FB_APP_ID")

FB_APP_SECRET = (
    os.getenv("FB_APP_SECRET")
    or META_APP_SECRET
)

FB_CONFIG_ID = os.getenv("FB_CONFIG_ID")

FB_REDIRECT_URI = os.getenv("FB_REDIRECT_URI")

FB_OAUTH_URL = (
    os.getenv("FB_OAUTH_URL")
    or "https://www.facebook.com/v26.0/dialog/oauth"
)

FB_TOKEN_URL = (
    os.getenv("FB_TOKEN_URL")
    or "https://graph.facebook.com/v26.0/oauth/access_token"
)

FB_GRAPH_URL = (
    os.getenv("FB_GRAPH_URL")
    or "https://graph.facebook.com/v26.0"
)

# Penyimpanan server-side sementara untuk tahap testing.
# Token TIDAK disimpan di cookie browser.
FACEBOOK_CONNECTION_STORE = {}

# State OAuth Facebook disimpan server-side.
# Ini membuat alur OAuth tetap bekerja saat URL login
# dibuat dari PowerShell lalu callback dibuka di browser.
FACEBOOK_OAUTH_STATE_STORE = {}


# =========================================================
# CREATE APPLICATION
# =========================================================

def create_app():

    app = Flask(__name__)


    # =====================================================
    # LOAD CONFIG
    # =====================================================

    app.config.from_object(
        Config
    )


    # =====================================================
    # VALIDATE SECRET KEY
    # =====================================================

    if not app.config.get(
        "SECRET_KEY"
    ):

        raise RuntimeError(
            "SECRET_KEY belum dikonfigurasi "
            "di file .env"
        )


    if not app.config.get(
        "JWT_SECRET_KEY"
    ):

        raise RuntimeError(
            "JWT_SECRET_KEY belum dikonfigurasi "
            "di file .env"
        )


    # =====================================================
    # SESSION CONFIGURATION
    # =====================================================

    app.config[
        "SESSION_COOKIE_HTTPONLY"
    ] = True

    app.config[
        "SESSION_COOKIE_SAMESITE"
    ] = "None"

    app.config[
        "SESSION_COOKIE_SECURE"
    ] = True

    app.config[
        "SESSION_COOKIE_PATH"
    ] = "/"


    # =====================================================
    # CORS
    # =====================================================

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://127.0.0.1:5173"
                ]
            }
        },
        supports_credentials=True,
        allow_headers=["Content-Type", 
    "ngrok-skip-browser-warning", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # =====================================================
    # DATABASE
    # =====================================================

    db.init_app(
        app
    )


    # =====================================================
    # JWT
    # =====================================================

    jwt.init_app(
        app
    )


    # =====================================================
    # CONTROLLERS
    # =====================================================

    from controllers import (
        auth_bp,
        dashboard_bp,
        meta_insight_bp,
        ai_analysis_bp,
        knowledge_base_bp,
        ai_content_planner_bp,
        sync_log_bp,
        report_bp,
        llm_chat_bp
    )

    from controllers.facebook_controller import facebook_bp


    # =====================================================
    # REGISTER BLUEPRINT
    # =====================================================

    app.register_blueprint(
        auth_bp
    )

    app.register_blueprint(
        dashboard_bp
    )

    app.register_blueprint(
        meta_insight_bp
    )

    app.register_blueprint(
        ai_analysis_bp
    )

    app.register_blueprint(
        knowledge_base_bp
    )

    app.register_blueprint(
        ai_content_planner_bp
    )

    app.register_blueprint(
        sync_log_bp
    )

    app.register_blueprint(
        report_bp
    )

    app.register_blueprint(
        llm_chat_bp
    )

    app.register_blueprint(
        facebook_bp
    )


    # =====================================================
    # ROOT
    # =====================================================

    @app.route(
        "/",
        methods=["GET"]
    )
    def index():

        return (
            "MAVis - Meta Analytical Visual"
        ), 200


    # =====================================================
    # META CONFIG TEST
    # =====================================================

    @app.route(
        "/api/meta/config",
        methods=["GET"]
    )
    def meta_config():

        return jsonify({

            "success": True,

            "data": {

                "app_id_exists":
                    bool(META_APP_ID),

                "app_secret_exists":
                    bool(META_APP_SECRET),

                "redirect_uri":
                    META_REDIRECT_URI,

                "oauth_url":
                    META_OAUTH_URL,

                "token_url":
                    META_TOKEN_URL,

                "graph_url":
                    META_GRAPH_URL,

                "scopes":
                    META_SCOPES

            }

        }), 200


    # =====================================================
    # META CONNECT
    # =====================================================

    @app.route(
        "/api/meta/connect",
        methods=["GET"]
    )
    @jwt_required_role("admin")
    def meta_connect():

        try:

            print("")
            print(
                "===================================="
            )
            print(
                "INSTAGRAM CONNECT START"
            )
            print(
                "===================================="
            )


            # ---------------------------------------------
            # VALIDASI CONFIG
            # ---------------------------------------------

            if not META_APP_ID:

                raise ValueError(
                    "META_APP_ID belum dikonfigurasi"
                )


            if not META_APP_SECRET:

                raise ValueError(
                    "META_APP_SECRET belum dikonfigurasi"
                )


            if not META_REDIRECT_URI:

                raise ValueError(
                    "META_REDIRECT_URI belum dikonfigurasi"
                )


            # ---------------------------------------------
            # STATE
            # ---------------------------------------------

            state = secrets.token_urlsafe(
                32
            )

            # Simpan ID user MAVis yang memulai OAuth.
            # Callback Instagram tidak membawa JWT, sehingga
            # identitas user harus dibawa melalui session.
            claims = get_jwt()

            mavis_user_id = claims.get("sub")

            if mavis_user_id is None:
                raise ValueError(
                    "User MAVis tidak ditemukan."
                )

            session[
                "meta_oauth_state"
            ] = state

            session[
                "meta_oauth_user_id"
            ] = int(mavis_user_id)


            # ---------------------------------------------
            # AUTHORIZATION URL
            # ---------------------------------------------

            params = {

                "client_id":
                    META_APP_ID,

                "redirect_uri":
                    META_REDIRECT_URI,

                "response_type":
                    "code",

                "scope":
                    META_SCOPES,

                "state":
                    state

            }


            authorization_url = (
                META_OAUTH_URL
                + "?"
                + urlencode(
                    params
                )
            )


            print(
                "META APP ID:",
                META_APP_ID
            )

            print(
                "REDIRECT URI:",
                META_REDIRECT_URI
            )

            print(
                "STATE:",
                state
            )

            print(
                "AUTH URL:",
                authorization_url
            )

            print(
                "===================================="
            )


            return jsonify({

                "success": True,

                "message":
                    "URL login Instagram berhasil dibuat",

                "data": {

                    "authorization_url":
                        authorization_url

                }

            }), 200


        except ValueError as e:

            print(
                "META CONNECT VALUE ERROR:",
                str(e)
            )

            return jsonify({

                "success": False,

                "message":
                    str(e)

            }), 400


        except Exception as e:

            print(
                "META CONNECT ERROR:",
                str(e)
            )

            return jsonify({

                "success": False,

                "message":
                    "Gagal membuat koneksi Instagram",

                "error":
                    str(e)

            }), 500


    # =====================================================
    # META CALLBACK
    # =====================================================

    @app.route(
        "/api/meta/callback",
        methods=["GET"]
    )
    def meta_callback():

        print("")
        print(
            "===================================="
        )
        print(
            "INSTAGRAM CALLBACK"
        )
        print(
            "===================================="
        )


        # =================================================
        # CEK ERROR DARI INSTAGRAM
        # =================================================

        error = request.args.get(
            "error"
        )

        error_reason = request.args.get(
            "error_reason"
        )

        error_description = request.args.get(
            "error_description"
        )


        if error:

            message = (
                error_description
                or error_reason
                or error
            )

            print(
                "INSTAGRAM OAUTH ERROR:",
                message
            )


            return render_template_string(
                """
                <!DOCTYPE html>

                <html>

                <head>
                    <meta charset="UTF-8">

                    <title>
                        MAVis
                    </title>
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

                        try {

                            if (
                                window.opener &&
                                !window.opener.closed
                            ) {

                                window.opener.postMessage(
                                    {
                                        type:
                                            "INSTAGRAM_OAUTH_ERROR",

                                        message:
                                            {{ message | tojson }}
                                    },

                                    "http://localhost:5173"
                                );

                            }

                        } catch (e) {

                            console.error(e);

                        }


                        setTimeout(
                            function () {

                                if (
                                    window.opener &&
                                    !window.opener.closed
                                ) {

                                    window.close();

                                } else {

                                    window.location.href =
                                        "http://localhost:5173/admin/meta-connection";

                                }

                            },
                            500
                        );

                    </script>

                </body>

                </html>
                """,

                message=message
            )


        # =================================================
        # AMBIL CODE
        # =================================================

        code = request.args.get(
            "code"
        )

        state = request.args.get(
            "state"
        )


        print(
            "CODE ADA:",
            bool(code)
        )

        print(
            "STATE ADA:",
            bool(state)
        )


        # =================================================
        # VALIDASI CODE
        # =================================================

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

                    <title>
                        MAVis
                    </title>
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

                        try {

                            if (
                                window.opener &&
                                !window.opener.closed
                            ) {

                                window.opener.postMessage(
                                    {
                                        type:
                                            "INSTAGRAM_OAUTH_ERROR",

                                        message:
                                            {{ message | tojson }}
                                    },

                                    "http://localhost:5173"
                                );

                            }

                        } catch (e) {

                            console.error(e);

                        }


                        setTimeout(
                            function () {

                                if (
                                    window.opener &&
                                    !window.opener.closed
                                ) {

                                    window.close();

                                } else {

                                    window.location.href =
                                        "http://localhost:5173/admin/meta-connection";

                                }

                            },
                            500
                        );

                    </script>

                </body>

                </html>
                """,

                message=message
            )


        # =================================================
        # VALIDASI STATE
        # =================================================

        stored_state = session.get(
            "meta_oauth_state"
        )

        print(
            "STORED STATE ADA:",
            bool(stored_state)
        )


        # -------------------------------------------------
        # Tetap mengikuti konfigurasi lama:
        # lanjut jika session state tidak tersedia.
        # -------------------------------------------------

        if (
            stored_state
            and state
            and stored_state != state
        ):

            print(
                "STATE TIDAK COCOK"
            )


            return render_template_string(
                """
                <!DOCTYPE html>

                <html>

                <head>
                    <meta charset="UTF-8">

                    <title>
                        MAVis
                    </title>
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
                            OAuth state tidak cocok.
                            Silakan ulangi koneksi.
                        </p>

                    </div>


                    <script>

                        try {

                            if (
                                window.opener &&
                                !window.opener.closed
                            ) {

                                window.opener.postMessage(
                                    {
                                        type:
                                            "INSTAGRAM_OAUTH_ERROR",

                                        message:
                                            "OAuth state tidak cocok."
                                    },

                                    "http://localhost:5173"
                                );

                            }

                        } catch (e) {

                            console.error(e);

                        }


                        setTimeout(
                            function () {

                                if (
                                    window.opener &&
                                    !window.opener.closed
                                ) {

                                    window.close();

                                } else {

                                    window.location.href =
                                        "http://localhost:5173/admin/meta-connection";

                                }

                            },
                            500
                        );

                    </script>

                </body>

                </html>
                """
            )


        # =================================================
        # TUKAR CODE MENJADI SHORT-LIVED TOKEN
        # =================================================

        try:

            token_response = requests.post(

                META_TOKEN_URL,

                data={

                    "client_id":
                        META_APP_ID,

                    "client_secret":
                        META_APP_SECRET,

                    "grant_type":
                        "authorization_code",

                    "redirect_uri":
                        META_REDIRECT_URI,

                    "code":
                        code

                },

                timeout=30

            )


            print(
                "TOKEN RESPONSE STATUS:",
                token_response.status_code
            )

            print(
                "TOKEN RESPONSE:",
                token_response.text
            )


            if not token_response.ok:

                raise RuntimeError(
                    "Gagal mendapatkan access token "
                    "Instagram: "
                    f"{token_response.text}"
                )


            token_data = (
                token_response.json()
            )


            short_token = (
                token_data.get(
                    "access_token"
                )
            )


            instagram_user_id = (
                token_data.get(
                    "user_id"
                )
            )


            if not short_token:

                raise RuntimeError(
                    "Access token Instagram "
                    "tidak ditemukan."
                )


            # =================================================
            # TUKAR KE LONG-LIVED TOKEN
            # =================================================

            exchange_response = (
                requests.get(

                    META_TOKEN_EXCHANGE_URL,

                    params={

                        "grant_type":
                            "ig_exchange_token",

                        "client_secret":
                            META_APP_SECRET,

                        "access_token":
                            short_token

                    },

                    timeout=30

                )
            )


            print(
                "LONG TOKEN STATUS:",
                exchange_response.status_code
            )

            print(
                "LONG TOKEN RESPONSE:",
                exchange_response.text
            )


            if exchange_response.ok:

                exchange_data = (
                    exchange_response.json()
                )


                access_token = (
                    exchange_data.get(
                        "access_token"
                    )
                    or short_token
                )


                expires_in = (
                    exchange_data.get(
                        "expires_in"
                    )
                )

            else:

                print(
                    "Long-lived token gagal."
                )

                print(
                    "Menggunakan short-lived token."
                )


                access_token = (
                    short_token
                )

                expires_in = 3600


            # =================================================
            # SIMPAN KONEKSI KE DATABASE
            # =================================================
            #
            # Token tidak lagi hanya disimpan di Flask session.
            # Database menjadi sumber permanen koneksi Instagram.
            # Session tetap dipakai untuk akun yang sedang aktif.
            # =================================================

            mavis_user_id = session.get(
                "meta_oauth_user_id"
            )

            if mavis_user_id is None:
                raise RuntimeError(
                    "User MAVis yang memulai OAuth tidak ditemukan."
                )

            mavis_user_id = int(
                mavis_user_id
            )

            # Ambil informasi akun Instagram.
            account_info = {}

            try:

                account_response = requests.get(
                    f"{META_GRAPH_URL}/v26.0/me",
                    params={
                        "fields": (
                            "user_id,"
                            "username,"
                            "name,"
                            "account_type,"
                            "profile_picture_url"
                        ),
                        "access_token": access_token
                    },
                    timeout=15
                )

                if account_response.ok:
                    account_info = (
                        account_response.json()
                    )
                else:
                    print(
                        "ACCOUNT INFO STATUS:",
                        account_response.status_code
                    )
                    print(
                        "ACCOUNT INFO RESPONSE:",
                        account_response.text
                    )

            except Exception as account_error:

                print(
                    "ACCOUNT INFO ERROR:",
                    str(account_error)
                )

            # Gunakan ID dari response token sebagai fallback.
            instagram_user_id = (
                account_info.get("user_id")
                or account_info.get("id")
                or instagram_user_id
            )

            if not instagram_user_id:
                raise RuntimeError(
                    "Instagram User ID tidak ditemukan."
                )

            instagram_username = (
                account_info.get("username")
            )

            account_type = (
                account_info.get("account_type")
            )

            profile_picture_url = (
                account_info.get(
                    "profile_picture_url"
                )
            )

            expires_at_db = None

            if expires_in:
                expires_at_db = (
                    datetime.utcnow()
                    +
                    timedelta(
                        seconds=int(expires_in)
                    )
                )

            # Cari koneksi berdasarkan user MAVis + akun Instagram.
            meta_connection = (
                Meta_Connections.query
                .filter_by(
                    user_id=mavis_user_id,
                    instagram_user_id=str(
                        instagram_user_id
                    )
                )
                .first()
            )

            if meta_connection:

                print(
                    "UPDATE KONEKSI INSTAGRAM:",
                    instagram_user_id
                )

                meta_connection.username = (
                    instagram_username
                )

                meta_connection.account_type = (
                    account_type
                )

                meta_connection.profile_picture_url = (
                    profile_picture_url
                )

                meta_connection.access_token = (
                    access_token
                )

                meta_connection.token_type = (
                    "Bearer"
                )

                meta_connection.expires_at = (
                    expires_at_db
                )

                meta_connection.connected = True

            else:

                print(
                    "SIMPAN KONEKSI INSTAGRAM BARU:",
                    instagram_user_id
                )

                meta_connection = Meta_Connections(
                    user_id=mavis_user_id,
                    instagram_user_id=str(
                        instagram_user_id
                    ),
                    username=instagram_username,
                    account_type=account_type,
                    profile_picture_url=(
                        profile_picture_url
                    ),
                    access_token=access_token,
                    token_type="Bearer",
                    expires_at=expires_at_db,
                    connected=True
                )

                db.session.add(
                    meta_connection
                )

            db.session.commit()

            print("")
            print(
                "===================================="
            )
            print(
                "META CONNECTION TERSIMPAN"
            )
            print(
                "===================================="
            )
            print(
                "MAVIS USER ID:",
                mavis_user_id
            )
            print(
                "INSTAGRAM USER ID:",
                instagram_user_id
            )
            print(
                "INSTAGRAM USERNAME:",
                instagram_username
            )
            print(
                "EXPIRES AT:",
                expires_at_db
            )
            print(
                "===================================="
            )

            # =================================================
            # SESSION
            # =================================================

            session[
                "meta_access_token"
            ] = access_token

            session[
                "meta_user_id"
            ] = str(instagram_user_id)

            session[
                "meta_username"
            ] = instagram_username

            session[
                "meta_token_expires_at"
            ] = (
                expires_at_db.isoformat()
                if expires_at_db
                else None
            )

            session[
                "meta_connected"
            ] = True

            # Akun yang baru selesai OAuth menjadi akun aktif.
            session[
                "meta_connection_id"
            ] = meta_connection.id

            # =================================================
            # HAPUS OAUTH STATE
            # =================================================

            session.pop(
                "meta_oauth_state",
                None
            )

            session.pop(
                "meta_oauth_user_id",
                None
            )

            session.modified = True


            print(
                "INSTAGRAM BERHASIL TERHUBUNG"
            )

            print(
                "INSTAGRAM USER ID:",
                instagram_user_id
            )


            # =================================================
            # RESULT
            # =================================================

            result = {

                "connected":
                    True,

                "instagram_user_id":
                    instagram_user_id,

                "expires_in":
                    expires_in

            }


            # =================================================
            # SUCCESS PAGE
            # =================================================
            #
            # Popup TIDAK diarahkan ke localhost.
            #
            # Popup mengirim pesan ke window utama
            # kemudian menutup dirinya sendiri.
            #
            # =================================================

            return render_template_string(
                """
                <!DOCTYPE html>

                <html>

                <head>

                    <meta charset="UTF-8">

                    <meta name="viewport"
                          content="width=device-width,
                                   initial-scale=1.0">

                    <title>
                        MAVis - Instagram
                    </title>

                </head>


                <body>

                    <div style="
                        font-family: Arial, sans-serif;
                        text-align: center;
                        margin-top: 100px;
                        padding: 20px;
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
                            Koneksi berhasil.
                            Window akan ditutup...
                        </p>

                    </div>


                    <script>

                        console.log(
                            "Instagram OAuth berhasil."
                        );


                        try {

                            // =================================================
                            // WINDOW UTAMA TERSEDIA
                            // =================================================

                            if (
                                window.opener &&
                                !window.opener.closed
                            ) {

                                console.log(
                                    "Mengirim pesan ke window utama..."
                                );


                                window.opener.postMessage(

                                    {
                                        type:
                                            "INSTAGRAM_OAUTH_SUCCESS",

                                        data:
                                            {{ result | tojson }}
                                    },

                                    "http://localhost:5173"

                                );


                                console.log(
                                    "Pesan OAuth berhasil dikirim."
                                );


                                // =================================================
                                // TUTUP POPUP
                                // =================================================

                                setTimeout(

                                    function () {

                                        console.log(
                                            "Menutup popup OAuth..."
                                        );

                                        window.close();

                                    },

                                    500

                                );


                            } else {

                                // =================================================
                                // FALLBACK
                                // =================================================

                                console.log(
                                    "window.opener tidak ditemukan."
                                );


                                setTimeout(

                                    function () {

                                        window.location.href =
                                            "http://localhost:5173/admin/meta-connection";

                                    },

                                    1000

                                );

                            }


                        } catch (e) {

                            console.error(
                                "OAuth callback error:",
                                e
                            );


                            setTimeout(

                                function () {

                                    if (
                                        window.opener &&
                                        !window.opener.closed
                                    ) {

                                        window.close();

                                    } else {

                                        window.location.href =
                                            "http://localhost:5173/admin/meta-connection";

                                    }

                                },

                                1000

                            );

                        }

                    </script>

                </body>

                </html>
                """,

                result=result

            )


        # =================================================
        # CALLBACK ERROR
        # =================================================

        except Exception as e:

            print(
                "INSTAGRAM CALLBACK ERROR:",
                str(e)
            )


            session.pop(
                "meta_oauth_state",
                None
            )

            session.pop(
                "meta_oauth_user_id",
                None
            )

            session.modified = True

            message = str(e)


            return render_template_string(
                """
                <!DOCTYPE html>

                <html>

                <head>

                    <meta charset="UTF-8">

                    <meta name="viewport"
                          content="width=device-width,
                                   initial-scale=1.0">

                    <title>
                        MAVis
                    </title>

                </head>


                <body>

                    <div style="
                        font-family: Arial;
                        text-align: center;
                        margin-top: 100px;
                        padding: 20px;
                    ">

                        <h2>
                            Koneksi Instagram gagal
                        </h2>


                        <p style="
                            color: #64748b;
                        ">
                            {{ message }}
                        </p>

                    </div>


                    <script>

                        try {

                            if (
                                window.opener &&
                                !window.opener.closed
                            ) {

                                window.opener.postMessage(

                                    {
                                        type:
                                            "INSTAGRAM_OAUTH_ERROR",

                                        message:
                                            {{ message | tojson }}
                                    },

                                    "http://localhost:5173"

                                );

                            }

                        } catch (e) {

                            console.error(
                                "Gagal mengirim error:",
                                e
                            );

                        }


                        setTimeout(

                            function () {

                                if (
                                    window.opener &&
                                    !window.opener.closed
                                ) {

                                    window.close();

                                } else {

                                    window.location.href =
                                        "http://localhost:5173/admin/meta-connection";

                                }

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
    # FACEBOOK HELPERS
    # =====================================================

    def facebook_appsecret_proof(access_token):

        if not access_token or not FB_APP_SECRET:
            return None

        return hmac.new(
            FB_APP_SECRET.encode("utf-8"),
            access_token.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()


    def facebook_graph_get(path, access_token, params=None):

        request_params = dict(params or {})
        request_params["access_token"] = access_token

        return requests.get(
            f"{FB_GRAPH_URL}{path}",
            params=request_params,
            timeout=30
        )


    def facebook_error_response(
        title,
        message,
        status_code=400,
        error=None
    ):

        payload = {
            "success": False,
            "message": message
        }

        if error is not None:
            payload["error"] = error

        return render_template_string(
            """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport"
                      content="width=device-width, initial-scale=1.0">
                <title>MAVis - Facebook</title>
            </head>
            <body>
                <div style="
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin-top: 100px;
                    padding: 20px;
                ">
                    <h2>{{ title }}</h2>
                    <p style="color:#64748b;">{{ message }}</p>
                </div>
                <script>
                    try {
                        if (window.opener && !window.opener.closed) {
                            window.opener.postMessage(
                                {
                                    type: "FACEBOOK_OAUTH_ERROR",
                                    message: {{ message | tojson }}
                                },
                                "http://localhost:5173"
                            );
                        }
                    } catch (e) {
                        console.error(e);
                    }

                    setTimeout(function () {
                        if (window.opener && !window.opener.closed) {
                            window.close();
                        } else {
                            window.location.href =
                                "http://localhost:5173/admin/meta-connection";
                        }
                    }, 1000);
                </script>
            </body>
            </html>
            """,
            title=title,
            message=message
        ), status_code


    # =====================================================
    # FACEBOOK CONNECT
    # =====================================================

    @app.route(
        "/api/facebook/connect",
        methods=["GET"]
    )
    @jwt_required_role("admin")
    def facebook_connect():

        try:

            if not FB_APP_ID:
                raise ValueError(
                    "FB_APP_ID belum dikonfigurasi di .env"
                )

            if not FB_APP_SECRET:
                raise ValueError(
                    "FB_APP_SECRET atau META_APP_SECRET belum dikonfigurasi"
                )

            if not FB_CONFIG_ID:
                raise ValueError(
                    "FB_CONFIG_ID belum dikonfigurasi di .env"
                )

            if not FB_REDIRECT_URI:
                raise ValueError(
                    "FB_REDIRECT_URI belum dikonfigurasi di .env"
                )

            claims = get_jwt()
            mavis_user_id = claims.get("sub")

            if mavis_user_id is None:
                raise ValueError(
                    "User MAVis tidak ditemukan."
                )

            state = secrets.token_urlsafe(32)

            # Simpan state Facebook di server, bukan session browser.
            # Dengan begitu URL yang dibuat lewat PowerShell tetap
            # dapat dilanjutkan di browser tanpa kehilangan state.
            FACEBOOK_OAUTH_STATE_STORE[state] = int(
                mavis_user_id
            )

            params = {
                "client_id": FB_APP_ID,
                "redirect_uri": FB_REDIRECT_URI,
                "config_id": FB_CONFIG_ID,
                "response_type": "code",
                "override_default_response_type": "true",
                "state": state
            }

            authorization_url = (
                FB_OAUTH_URL
                + "?"
                + urlencode(params)
            )

            print("")
            print("====================================")
            print("FACEBOOK CONNECT START")
            print("====================================")
            print("FB APP ID:", FB_APP_ID)
            print("FB CONFIG ID:", FB_CONFIG_ID)
            print("FB REDIRECT URI:", FB_REDIRECT_URI)
            print("STATE:", state)
            print("====================================")

            return jsonify({
                "success": True,
                "message": "URL login Facebook berhasil dibuat",
                "data": {
                    "authorization_url": authorization_url
                }
            }), 200

        except ValueError as e:

            return jsonify({
                "success": False,
                "message": str(e)
            }), 400

        except Exception as e:

            print("FACEBOOK CONNECT ERROR:", str(e))

            return jsonify({
                "success": False,
                "message": "Gagal membuat koneksi Facebook",
                "error": str(e)
            }), 500


    # =====================================================
    # FACEBOOK CALLBACK
    # =====================================================

    @app.route(
        "/api/facebook/callback",
        methods=["GET"]
    )
    def facebook_callback():

        try:

            error = request.args.get("error")
            error_reason = request.args.get("error_reason")
            error_description = request.args.get(
                "error_description"
            )

            if error:
                message = (
                    error_description
                    or error_reason
                    or error
                )

                print(
                    "FACEBOOK OAUTH ERROR:",
                    message
                )

                return facebook_error_response(
                    "Koneksi Facebook gagal",
                    message
                )

            code = request.args.get("code")
            state = request.args.get("state")

            if not code:
                return facebook_error_response(
                    "Koneksi Facebook gagal",
                    "Authorization code Facebook tidak ditemukan."
                )

            # Validasi state dari penyimpanan server-side.
            # State dihapus saat diambil sehingga hanya dapat digunakan sekali.
            mavis_user_id = FACEBOOK_OAUTH_STATE_STORE.pop(
                state,
                None
            ) if state else None

            if mavis_user_id is None:
                return facebook_error_response(
                    "Koneksi Facebook gagal",
                    "OAuth state tidak cocok, sudah digunakan, atau tidak berlaku. Silakan ulangi koneksi."
                )

            # ---------------------------------------------
            # TUKAR CODE -> SYSTEM USER ACCESS TOKEN
            # ---------------------------------------------

            token_response = requests.get(
                FB_TOKEN_URL,
                params={
                    "client_id": FB_APP_ID,
                    "client_secret": FB_APP_SECRET,
                    "redirect_uri": FB_REDIRECT_URI,
                    "code": code
                },
                timeout=30
            )

            print(
                "FACEBOOK TOKEN STATUS:",
                token_response.status_code
            )
            print(
                "FACEBOOK TOKEN RESPONSE RECEIVED"
            )

            if not token_response.ok:
                raise RuntimeError(
                    "Gagal mendapatkan access token Facebook: "
                    f"{token_response.text}"
                )

            token_data = token_response.json()

            system_user_token = token_data.get(
                "access_token"
            )

            expires_in = token_data.get(
                "expires_in"
            )

            if not system_user_token:
                raise RuntimeError(
                    "Access token Facebook tidak ditemukan."
                )

            # ---------------------------------------------
            # AMBIL IDENTITAS TOKEN
            # ---------------------------------------------

            me_response = facebook_graph_get(
                "/me",
                system_user_token,
                {
                    "fields": "id,name"
                }
            )

            try:
                me_data = me_response.json()
            except Exception:
                me_data = {
                    "raw_response": me_response.text
                }

            print(
                "FACEBOOK /ME STATUS:",
                me_response.status_code
            )
            print(
                "FACEBOOK /ME RESPONSE:",
                me_data
            )

            # ---------------------------------------------
            # AMBIL FACEBOOK PAGES
            # ---------------------------------------------

            pages_response = facebook_graph_get(
                "/me/accounts",
                system_user_token,
                {
                    "fields": (
                        "id,name,access_token,category,tasks"
                    )
                }
            )

            try:
                pages_data = pages_response.json()
            except Exception:
                pages_data = {
                    "raw_response": pages_response.text
                }

            print(
                "FACEBOOK /ME/ACCOUNTS STATUS:",
                pages_response.status_code
            )
            print(
                "FACEBOOK /ME/ACCOUNTS DATA COUNT:",
                len(pages_data.get("data", []))
            )

            if not pages_response.ok:
                raise RuntimeError(
                    "Gagal mengambil daftar Facebook Page: "
                    f"{pages_data}"
                )

            pages = pages_data.get("data", [])

            # ---------------------------------------------
            # SIMPAN KONEKSI FACEBOOK KE DATABASE
            # ---------------------------------------------
            #
            # Database menjadi sumber permanen koneksi Facebook.
            # Store di memory tetap dipertahankan sebagai fallback
            # agar alur OAuth lama tidak langsung berubah.
            # ---------------------------------------------

            from services.facebook_service import (
                FacebookService
            )

            facebook_user = {
                "id": me_data.get("id"),
                "name": me_data.get("name")
            }

            saved_connections = (
                FacebookService
                .save_connections(
                    mavis_user_id=int(mavis_user_id),
                    facebook_user=facebook_user,
                    pages=pages,
                    expires_in=expires_in
                )
            )

            # ---------------------------------------------
            # SERVER-SIDE FALLBACK / COMPATIBILITY
            # ---------------------------------------------

            FACEBOOK_CONNECTION_STORE[int(mavis_user_id)] = {
                "system_user_token": system_user_token,
                "facebook_user_id": (
                    me_data.get("id")
                ),
                "facebook_user_name": (
                    me_data.get("name")
                ),
                "expires_in": expires_in,
                "pages": pages,
                "selected_page": (
                    pages[0] if pages else None
                ),
                "database_connections": saved_connections
            }

            print(
                "FACEBOOK CONNECTION SAVED:",
                len(saved_connections)
            )

            # State OAuth sudah dihapus ketika callback mengambilnya.

            selected_page = (
                pages[0] if pages else None
            )

            result = {
                "connected": True,
                "facebook_user_id": me_data.get("id"),
                "facebook_user_name": me_data.get("name"),
                "expires_in": expires_in,
                "pages": [
                    {
                        "id": page.get("id"),
                        "name": page.get("name"),
                        "category": page.get("category"),
                        "tasks": page.get("tasks", [])
                    }
                    for page in pages
                ],
                "selected_page": (
                    {
                        "id": selected_page.get("id"),
                        "name": selected_page.get("name")
                    }
                    if selected_page
                    else None
                )
            }

            return render_template_string(
                """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport"
                          content="width=device-width, initial-scale=1.0">
                    <title>MAVis - Facebook</title>
                </head>
                <body>
                    <div style="
                        font-family: Arial, sans-serif;
                        text-align: center;
                        margin-top: 100px;
                        padding: 20px;
                    ">
                        <div style="
                            width:64px;height:64px;border-radius:50%;
                            background:#22c55e;color:white;
                            display:flex;align-items:center;
                            justify-content:center;margin:0 auto 20px;
                            font-size:34px;
                        ">✓</div>
                        <h2>Facebook berhasil terhubung</h2>
                        <p style="color:#64748b;">
                            Koneksi Facebook berhasil. Window akan ditutup...
                        </p>
                    </div>
                    <script>
                        try {
                            if (window.opener && !window.opener.closed) {
                                window.opener.postMessage(
                                    {
                                        type: "FACEBOOK_OAUTH_SUCCESS",
                                        data: {{ result | tojson }}
                                    },
                                    "http://localhost:5173"
                                );
                                setTimeout(function(){ window.close(); }, 500);
                            } else {
                                setTimeout(function(){
                                    window.location.href =
                                        "http://localhost:5173/admin/meta-connection";
                                }, 1000);
                            }
                        } catch (e) {
                            console.error(e);
                            setTimeout(function(){ window.close(); }, 1000);
                        }
                    </script>
                </body>
                </html>
                """,
                result=result
            )

        except Exception as e:

            print(
                "FACEBOOK CALLBACK ERROR:",
                str(e)
            )

            return facebook_error_response(
                "Koneksi Facebook gagal",
                str(e),
                500
            )


    # =====================================================
    # META STATUS
    # =====================================================

    @app.route(
        "/api/meta/status",
        methods=["GET"]
    )
    @jwt_required_role(
        "admin",
        "manager"
    )
    def meta_status():

        try:

            # =================================================
            # AMBIL USER MAVis DARI JWT
            # =================================================

            claims = get_jwt()

            mavis_user_id = claims.get("sub")

            if mavis_user_id is None:
                return jsonify({
                    "success": False,
                    "message": "User MAVis tidak ditemukan."
                }), 401

            mavis_user_id = int(
                mavis_user_id
            )

            # =================================================
            # AMBIL AKUN INSTAGRAM AKTIF
            # =================================================

            meta_connection_id = session.get(
                "meta_connection_id"
            )

            meta_connection = None

            if meta_connection_id:

                meta_connection = (
                    Meta_Connections.query
                    .filter_by(
                        id=int(meta_connection_id),
                        user_id=mavis_user_id
                    )
                    .first()
                )

            # Jika session tidak memiliki akun aktif,
            # gunakan koneksi terakhir yang masih aktif.
            if meta_connection is None:

                meta_connection = (
                    Meta_Connections.query
                    .filter_by(
                        user_id=mavis_user_id,
                        connected=True
                    )
                    .order_by(
                        Meta_Connections.updated_at.desc()
                    )
                    .first()
                )

            access_token = (
                meta_connection.access_token
                if meta_connection
                else None
            )

            instagram_user_id = (
                meta_connection.instagram_user_id
                if meta_connection
                else None
            )

            expires_at = (
                meta_connection.expires_at.isoformat()
                if meta_connection
                and meta_connection.expires_at
                else None
            )


            print("")

            print(
                "===================================="
            )

            print(
                "META STATUS"
            )

            print(
                "TOKEN ADA:",
                bool(access_token)
            )

            print(
                "USER ID:",
                instagram_user_id
            )

            print(
                "===================================="
            )


            # =================================================
            # BELUM TERHUBUNG
            # =================================================

            if not access_token:

                return jsonify({

                    "success": True,

                    "message":
                        "Instagram belum terhubung",

                    "data": {

                        "connected":
                            False,

                        "instagram_user_id":
                            None,

                        "expires_at":
                            None,

                        "account":
                            None

                    }

                }), 200


            # =================================================
            # AMBIL DATA AKUN INSTAGRAM
            # =================================================

            account = None

            account_error = None


            try:

                account_response = requests.get(

                    f"{META_GRAPH_URL}/v26.0/me",

                    params={

                        "fields": (
                            "user_id,"
                            "username,"
                            "name,"
                            "account_type,"
                            "profile_picture_url,"
                            "followers_count,"
                            "follows_count,"
                            "media_count"
                        ),

                        "access_token":
                            access_token

                    },

                    timeout=30

                )


                print(
                    "ACCOUNT STATUS:",
                    account_response.status_code
                )


                try:

                    account_result = (
                        account_response.json()
                    )

                except Exception:

                    account_result = {

                        "raw_response":
                            account_response.text

                    }


                print(
                    "ACCOUNT RESPONSE:",
                    account_result
                )


                if account_response.ok:

                    account = account_result

                else:

                    account_error = account_result


            except Exception as e:

                account_error = str(e)

                print(
                    "ACCOUNT REQUEST ERROR:",
                    str(e)
                )


            # =================================================
            # TOKEN INVALID / EXPIRED
            # =================================================

            if account is None and account_error:

                error_text = (
                    str(account_error).lower()
                )


                if (
                    "token" in error_text
                    or "oauth" in error_text
                    or "expired" in error_text
                    or "invalid" in error_text
                ):

                    return jsonify({

                        "success": False,

                        "message":
                            "Token Instagram tidak valid "
                            "atau sudah kedaluwarsa",

                        "data": {

                            "connected":
                                False,

                            "instagram_user_id":
                                instagram_user_id,

                            "expires_at":
                                expires_at,

                            "account":
                                None

                        },

                        "error":
                            account_error

                    }), 401


            # =================================================
            # NORMALISASI DATA AKUN
            # =================================================

            if account is None:

                account = {

                    "user_id":
                        instagram_user_id

                }


            actual_user_id = (

                account.get("user_id")

                or account.get("id")

                or instagram_user_id

            )


            # =================================================
            # SIMPAN USER ID
            # =================================================

            if actual_user_id:

                session[
                    "meta_user_id"
                ] = actual_user_id

                session[
                    "meta_connected"
                ] = True

                if meta_connection:

                    meta_connection.instagram_user_id = str(
                        actual_user_id
                    )

                    meta_connection.username = (
                        account.get("username")
                        or meta_connection.username
                    )

                    meta_connection.account_type = (
                        account.get("account_type")
                        or meta_connection.account_type
                    )

                    meta_connection.profile_picture_url = (
                        account.get("profile_picture_url")
                        or meta_connection.profile_picture_url
                    )

                    meta_connection.connected = True

                    db.session.commit()

                session.modified = True


            # =================================================
            # RESPONSE
            # =================================================

            return jsonify({

                "success": True,

                "message":
                    "Status koneksi Instagram berhasil diambil",

                "data": {

                    "connected":
                        True,

                    "instagram_user_id":
                        actual_user_id,

                    "expires_at":
                        expires_at,

                    "account":
                        account

                }

            }), 200


        except Exception as e:

            print(
                "META STATUS ERROR:",
                str(e)
            )


            return jsonify({

                "success": False,

                "message":
                    "Gagal mengambil status koneksi Instagram",

                "error":
                    str(e)

            }), 500


    # =====================================================
    # META DISCONNECT
    # =====================================================

    @app.route(
        "/api/meta/disconnect",
        methods=["POST"]
    )
    @jwt_required_role(
        "admin"
    )
    def meta_disconnect():

        try:

            # =================================================
            # PUTUSKAN AKUN INSTAGRAM AKTIF
            # =================================================

            claims = get_jwt()

            mavis_user_id = claims.get("sub")

            if mavis_user_id is not None:

                mavis_user_id = int(
                    mavis_user_id
                )

            meta_connection_id = session.get(
                "meta_connection_id"
            )

            meta_connection = None

            if (
                meta_connection_id
                and mavis_user_id is not None
            ):

                meta_connection = (
                    Meta_Connections.query
                    .filter_by(
                        id=int(meta_connection_id),
                        user_id=mavis_user_id
                    )
                    .first()
                )

            if meta_connection:

                meta_connection.connected = False

                db.session.commit()

            # Session hanya dihapus untuk akun aktif.
            session.pop(
                "meta_access_token",
                None
            )

            session.pop(
                "meta_account_id",
                None
            )

            session.pop(
                "meta_user_id",
                None
            )

            session.pop(
                "meta_username",
                None
            )

            session.pop(
                "meta_token_expires_at",
                None
            )

            session.pop(
                "meta_token_expires_in",
                None
            )

            session.pop(
                "meta_connected",
                None
            )

            session.pop(
                "meta_connection_id",
                None
            )

            session.pop(
                "meta_oauth_state",
                None
            )

            session.modified = True


            # =================================================
            # CATAT STATUS DISCONNECTED KE SYNC LOG
            # =================================================
            #
            # Data Instagram lama TIDAK dihapus.
            # Log ini digunakan sebagai status koneksi bersama
            # yang dapat dibaca oleh Dashboard.
            #
            # =================================================

            from models import SyncLog

            disconnect_log = SyncLog(
                sync_date=datetime.utcnow(),
                total_posts=0,
                status="DISCONNECTED",
                message=(
                    "Koneksi Instagram diputuskan "
                    "oleh pengguna."
                )
            )

            db.session.add(
                disconnect_log
            )

            db.session.commit()


            # =================================================
            # RESPONSE
            # =================================================

            return jsonify({

                "success": True,

                "message":
                    "Instagram berhasil diputuskan",

                "data": {

                    "connected":
                        False

                }

            }), 200


        except Exception as e:

            db.session.rollback()

            print(
                "META DISCONNECT ERROR:",
                str(e)
            )

            return jsonify({

                "success": False,

                "message":
                    "Gagal memutuskan Instagram",

                "error":
                    str(e)

            }), 500


    # =====================================================
    # META SYNCHRONIZE
    # =====================================================

    @app.route(
        "/api/meta/synchronize",
        methods=["POST"]
    )
    @jwt_required_role(
        "admin"
    )
    def meta_synchronize():

        try:

            claims = get_jwt()

            mavis_user_id = claims.get("sub")

            if mavis_user_id is None:

                return jsonify({
                    "success": False,
                    "message": "User MAVis tidak ditemukan."
                }), 401

            mavis_user_id = int(
                mavis_user_id
            )

            meta_connection_id = session.get(
                "meta_connection_id"
            )

            meta_connection = None

            if meta_connection_id:

                meta_connection = (
                    Meta_Connections.query
                    .filter_by(
                        id=int(meta_connection_id),
                        user_id=mavis_user_id,
                        connected=True
                    )
                    .first()
                )

            if meta_connection is None:

                meta_connection = (
                    Meta_Connections.query
                    .filter_by(
                        user_id=mavis_user_id,
                        connected=True
                    )
                    .order_by(
                        Meta_Connections.updated_at.desc()
                    )
                    .first()
                )

            access_token = (
                meta_connection.access_token
                if meta_connection
                else session.get(
                    "meta_access_token"
                )
            )

            if not access_token:

                return jsonify({

                    "success": False,

                    "message":
                        "Instagram belum terhubung"

                }), 400

            # Pastikan service lama tetap dapat membaca
            # akun aktif melalui session.
            session[
                "meta_access_token"
            ] = access_token

            if meta_connection:

                session[
                    "meta_connection_id"
                ] = meta_connection.id

                session[
                    "meta_user_id"
                ] = meta_connection.instagram_user_id

                session[
                    "meta_username"
                ] = meta_connection.username

                session[
                    "meta_token_expires_at"
                ] = (
                    meta_connection.expires_at.isoformat()
                    if meta_connection.expires_at
                    else None
                )

                session[
                    "meta_connected"
                ] = True

                session.modified = True


            from services.meta_connection_service import (
                MetaConnectionService
            )


            result = (
                MetaConnectionService
                .synchronize()
            )


            return jsonify({

                "success": True,

                "message":
                    "Sinkronisasi Instagram berhasil",

                "data":
                    result

            }), 200


        except ValueError as e:

            return jsonify({

                "success": False,

                "message":
                    str(e)

            }), 400


        except Exception as e:

            print(
                "SYNC ERROR:",
                str(e)
            )


            return jsonify({

                "success": False,

                "message":
                    "Sinkronisasi Instagram gagal",

                "error":
                    str(e)

            }), 500


    # =====================================================
    # TEST DATABASE
    # =====================================================

    @app.route(
        "/test-db",
        methods=["GET"]
    )
    def test_db():

        try:

            db.session.execute(
                text("SELECT 1")
            )


            return {

                "success":
                    True,

                "message":
                    (
                        "Database MAVis "
                        "berhasil terhubung"
                    )

            }, 200


        except Exception as e:

            return {

                "success":
                    False,

                "message":
                    (
                        "Koneksi database gagal"
                    ),

                "error":
                    str(e)

            }, 500


    # =====================================================
    # TEST MODELS
    # =====================================================

    @app.route(
        "/test-models",
        methods=["GET"]
    )
    def test_models():

        try:

            from models import (

                Users,

                Posts,

                Post_Metrics,

                Account_Metrics,

                Clusters,

                Forecast,

                Knowledge_Base,

                Embeddings,

                Recommendations,

                Content_Pillar,

                AIDAStage,

                ContentRecommendations,

                SyncLog,

                Reports,

                Report_Evaluations,

                Report_Approvals,

                Meta_Connections

            )


            data = {

                "users":
                    Users.query.count(),

                "posts":
                    Posts.query.count(),

                "post_metrics":
                    Post_Metrics.query.count(),

                "account_metrics":
                    Account_Metrics.query.count(),

                "clusters":
                    Clusters.query.count(),

                "forecast":
                    Forecast.query.count(),

                "knowledge_base":
                    Knowledge_Base.query.count(),

                "embeddings":
                    Embeddings.query.count(),

                "recommendations":
                    Recommendations.query.count(),

                "content_pillar":
                    Content_Pillar.query.count(),

                "aida_stage":
                    AIDAStage.query.count(),

                "content_recommendations":
                    ContentRecommendations.query.count(),

                "sync_log":
                    SyncLog.query.count(),

                "reports":
                    Reports.query.count(),

                "report_evaluations":
                    Report_Evaluations.query.count(),

                "report_approvals":
                    Report_Approvals.query.count(),

                "meta_connections":
                    Meta_Connections.query.count()

            }


            return {

                "success":
                    True,

                "message":
                    (
                        "Semua model berhasil "
                        "terhubung ke database"
                    ),

                "data":
                    data

            }, 200


        except Exception as e:

            return {

                "success":
                    False,

                "message":
                    "Model gagal terhubung",

                "error":
                    str(e)

            }, 500


    # =====================================================
    # TEST FLASK SESSION
    # =====================================================

    @app.route(
        "/test-session",
        methods=["GET"]
    )
    def test_session():

        try:

            session[
                "mavis_test"
            ] = True


            return {

                "success":
                    True,

                "message":
                    (
                        "Flask session berhasil"
                    ),

                "session_value":
                    session.get(
                        "mavis_test"
                    )

            }, 200


        except Exception as e:

            return {

                "success":
                    False,

                "message":
                    "Flask session gagal",

                "error":
                    str(e)

            }, 500


    # =====================================================
    # RETURN APP
    # =====================================================

    return app


# =========================================================
# CREATE APP
# =========================================================

app = create_app()


# =========================================================
# IMPORT MODELS
# =========================================================

from models import (

    Users,

    Posts,

    Post_Metrics,

    Account_Metrics,

    Clusters,

    Forecast,

    Knowledge_Base,

    Embeddings,

    Recommendations,

    Content_Pillar,

    AIDAStage,

    ContentRecommendations,

    SyncLog,

    Reports,

    Report_Evaluations,

    Report_Approvals,

    Meta_Connections,

    Facebook_Connections,
    Facebook_Insights,
    Facebook_Contents

)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )