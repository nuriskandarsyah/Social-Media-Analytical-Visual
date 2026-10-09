import os
import secrets
import requests
import time

from datetime import datetime
from urllib.parse import urlencode
from flask import session

from extensions import db
from models import (
    Posts,
    Post_Metrics,
    Account_Metrics,
    SyncLog,
    Clusters,
    Forecast
)


class MetaConnectionService:

    # =========================================================
    # CONFIG
    # =========================================================

    APP_ID = os.getenv(
        "META_APP_ID",
        ""
    ).strip()

    APP_SECRET = os.getenv(
        "META_APP_SECRET",
        ""
    ).strip()

    ACCESS_TOKEN = os.getenv(
        "META_ACCESS_TOKEN",
        ""
    ).strip()

    ACCOUNT_ID = os.getenv(
        "META_ACCOUNT_ID",
        ""
    ).strip()

    REDIRECT_URI = os.getenv(
        "META_REDIRECT_URI",
        "http://127.0.0.1:5000/api/meta/callback"
    ).strip()

    OAUTH_URL = os.getenv(
        "META_OAUTH_URL",
        "https://www.instagram.com/oauth/authorize"
    ).strip()

    TOKEN_URL = os.getenv(
        "META_TOKEN_URL",
        "https://api.instagram.com/oauth/access_token"
    ).strip()


    # =========================================================
    # SCOPES
    # =========================================================

    SCOPES = [
        "instagram_business_basic",
        "instagram_business_manage_insights",
    ]


    # =========================================================
    # GET ACCESS TOKEN
    # =========================================================

    @classmethod
    def get_access_token(cls):

        return (
            session.get(
                "meta_access_token"
            )
            or cls.ACCESS_TOKEN
        )


    # =========================================================
    # GET ACCOUNT ID
    # =========================================================

    @classmethod
    def get_account_id(cls):

        return (
            session.get(
                "meta_account_id"
            )
            or cls.ACCOUNT_ID
        )


    # =========================================================
    # VALIDATE CONFIG
    # =========================================================

    @classmethod
    def validate_config(cls):

        missing = []

        if not cls.APP_ID:
            missing.append(
                "META_APP_ID"
            )

        if not cls.APP_SECRET:
            missing.append(
                "META_APP_SECRET"
            )

        if not cls.REDIRECT_URI:
            missing.append(
                "META_REDIRECT_URI"
            )

        if not cls.OAUTH_URL:
            missing.append(
                "META_OAUTH_URL"
            )

        if not cls.TOKEN_URL:
            missing.append(
                "META_TOKEN_URL"
            )

        if missing:

            raise ValueError(
                "Konfigurasi Meta belum lengkap: "
                + ", ".join(missing)
            )

        return True


    # =========================================================
    # CREATE OAUTH URL
    # =========================================================

    @classmethod
    def get_authorization_url(cls):

        cls.validate_config()

        state = secrets.token_urlsafe(
            32
        )

        session[
            "meta_oauth_state"
        ] = state

        params = {

            "client_id":
                cls.APP_ID,

            "redirect_uri":
                cls.REDIRECT_URI,

            "response_type":
                "code",

            "scope":
                ",".join(
                    cls.SCOPES
                ),

            "state":
                state,
        }

        return (
            cls.OAUTH_URL
            + "?"
            + urlencode(params)
        )


    # =========================================================
    # VALIDATE OAUTH STATE
    # =========================================================

    @classmethod
    def validate_state(
        cls,
        received_state
    ):

        saved_state = session.get(
            "meta_oauth_state"
        )

        if not saved_state:

            raise ValueError(
                "OAuth state tidak ditemukan."
            )

        if not received_state:

            raise ValueError(
                "OAuth state tidak diberikan."
            )

        if saved_state != received_state:

            raise ValueError(
                "OAuth state tidak valid."
            )

        session.pop(
            "meta_oauth_state",
            None
        )

        return True


    # =========================================================
    # EXCHANGE AUTHORIZATION CODE
    # =========================================================

    @classmethod
    def exchange_code_for_token(
        cls,
        code
    ):

        cls.validate_config()

        if not code:

            raise ValueError(
                "Authorization code tidak ditemukan."
            )

        payload = {

            "client_id":
                cls.APP_ID,

            "client_secret":
                cls.APP_SECRET,

            "grant_type":
                "authorization_code",

            "redirect_uri":
                cls.REDIRECT_URI,

            "code":
                code,
        }

        response = requests.post(
            cls.TOKEN_URL,
            data=payload,
            timeout=30
        )

        try:

            result = response.json()

        except Exception:

            result = {
                "raw_response":
                    response.text
            }

        if not response.ok:

            raise RuntimeError(
                "Gagal menukar authorization code. "
                f"HTTP {response.status_code}: "
                f"{result}"
            )

        if not result.get(
            "access_token"
        ):

            raise RuntimeError(
                "Meta tidak mengembalikan "
                "access token: "
                f"{result}"
            )

        return result


    # =========================================================
    # GET LONG-LIVED TOKEN
    # =========================================================

    @classmethod
    def get_long_lived_token(
        cls,
        short_lived_token
    ):

        if not short_lived_token:

            raise ValueError(
                "Short-lived access token kosong."
            )

        url = (
            "https://graph.instagram.com/"
            "access_token"
        )

        params = {

            "grant_type":
                "ig_exchange_token",

            "client_secret":
                cls.APP_SECRET,

            "access_token":
                short_lived_token,
        }

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        try:

            result = response.json()

        except Exception:

            result = {
                "raw_response":
                    response.text
            }

        if not response.ok:

            raise RuntimeError(
                "Gagal mendapatkan "
                "long-lived token. "
                f"HTTP {response.status_code}: "
                f"{result}"
            )

        if not result.get(
            "access_token"
        ):

            raise RuntimeError(
                "Meta tidak mengembalikan "
                "long-lived access token: "
                f"{result}"
            )

        return result


    # =========================================================
    # GET INSTAGRAM ACCOUNT
    # =========================================================

    @classmethod
    def get_account_info(
        cls,
        access_token
    ):

        if not access_token:

            raise ValueError(
                "Access token kosong."
            )

        url = (
            "https://graph.instagram.com/"
            "v26.0/me"
        )

        params = {

            "fields":
                (
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
                access_token,
        }

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        try:

            result = response.json()

        except Exception:

            result = {
                "raw_response":
                    response.text
            }

        if not response.ok:

            raise RuntimeError(
                "Gagal mengambil informasi "
                "akun Instagram. "
                f"HTTP {response.status_code}: "
                f"{result}"
            )

        return result


    # =========================================================
    # GET MEDIA
    # =========================================================

    @classmethod
    def get_media(
        cls,
        account_id,
        access_token,
        limit=100
    ):

        if not account_id:
            raise ValueError(
                "Instagram Account ID kosong."
            )

        if not access_token:
            raise ValueError(
                "Access token kosong."
            )

        # Meta/Instagram API menggunakan pagination.
        # Limit hanya menentukan jumlah item per halaman.
        # Semua halaman diambil melalui paging.next.
        url = (
            "https://graph.instagram.com/"
            f"v26.0/{account_id}/media"
        )

        params = {
            "access_token": access_token,
            "fields": (
                "id,"
                "caption,"
                "media_type,"
                "media_url,"
                "permalink,"
                "thumbnail_url,"
                "timestamp,"
                "media_product_type,"
                "collaboration"
            ),
            "limit": min(int(limit or 100), 100),
        }

        all_media = []
        page_number = 0

        try:
            while url:

                page_number += 1

                response = requests.get(
                    url,
                    params=params,
                    timeout=30
                )

                try:
                    result = response.json()
                except Exception:
                    result = {
                        "raw_response": response.text
                    }

                if not response.ok:
                    raise RuntimeError(
                        "Gagal mengambil media Instagram. "
                        f"HTTP {response.status_code}: "
                        f"{result}"
                    )

                current_data = result.get("data", [])

                if not isinstance(current_data, list):
                    current_data = []

                all_media.extend(current_data)

                print(
                    f"MEDIA PAGE {page_number}: "
                    f"{len(current_data)} media | "
                    f"TOTAL TERKUMPUL: {len(all_media)}"
                )

                paging = result.get("paging") or {}
                next_url = paging.get("next")

                if next_url:
                    url = next_url
                    # paging.next sudah membawa parameter request.
                    params = None
                else:
                    url = None

            print(
                "TOTAL MEDIA INSTAGRAM:",
                len(all_media)
            )

            return {
                "data": all_media,
                "paging": {}
            }

        except requests.exceptions.RequestException as e:
            print(
                "GET MEDIA ERROR:",
                repr(e)
            )

            raise RuntimeError(
                "Gagal mengambil media Instagram: "
                f"{e}"
            )


    # =========================================================
    # CONNECT META
    # =========================================================

    @classmethod
    def connect_meta_account(cls):

        authorization_url = (
            cls.get_authorization_url()
        )

        return {

            "connected":
                False,

            "authorization_required":
                True,

            "authorization_url":
                authorization_url,

            "redirect_uri":
                cls.REDIRECT_URI,

        }


    # =========================================================
    # CALLBACK
    # =========================================================

    @classmethod
    def handle_callback(
        cls,
        code,
        state
    ):

        # -----------------------------------------------------
        # 1. VALIDASI STATE
        # -----------------------------------------------------

        cls.validate_state(
            state
        )


        # -----------------------------------------------------
        # 2. CODE -> SHORT TOKEN
        # -----------------------------------------------------

        token_result = (
            cls.exchange_code_for_token(
                code
            )
        )

        short_lived_token = (
            token_result.get(
                "access_token"
            )
        )


        # -----------------------------------------------------
        # 3. SHORT TOKEN -> LONG TOKEN
        # -----------------------------------------------------

        long_lived_result = (
            cls.get_long_lived_token(
                short_lived_token
            )
        )

        access_token = (
            long_lived_result.get(
                "access_token"
            )
        )

        if not access_token:

            raise RuntimeError(
                "Long-lived access token tidak ditemukan."
            )


        # -----------------------------------------------------
        # 4. AMBIL ACCOUNT
        # -----------------------------------------------------

        account = (
            cls.get_account_info(
                access_token
            )
        )

        account_id = (

            account.get(
                "user_id"
            )

            or

            account.get(
                "id"
            )

        )

        username = (
            account.get(
                "username"
            )
        )

        if not account_id:

            raise RuntimeError(
                "Instagram user_id tidak ditemukan."
            )

        if not username:

            raise RuntimeError(
                "Instagram username tidak ditemukan."
            )


        # -----------------------------------------------------
        # 5. SIMPAN SESSION
        # -----------------------------------------------------

        session[
            "meta_access_token"
        ] = access_token

        session[
            "meta_account_id"
        ] = account_id

        session[
            "meta_username"
        ] = username

        session[
            "meta_connected"
        ] = True

        session[
            "meta_token_expires_in"
        ] = (
            long_lived_result.get(
                "expires_in"
            )
        )

        session.modified = True


        print(
            "================================"
        )

        print(
            "INSTAGRAM OAUTH SUCCESS"
        )

        print(
            "Account ID:",
            account_id
        )

        print(
            "Username:",
            username
        )

        print(
            "Token tersedia:",
            bool(access_token)
        )

        print(
            "Session connected:",
            session.get(
                "meta_connected"
            )
        )

        print(
            "================================"
        )


        # -----------------------------------------------------
        # 6. RESPONSE
        # -----------------------------------------------------

        return {

            "connected":
                True,

            "account_id":
                account_id,

            "username":
                username,

            "account":
                account,

            "token_received":
                bool(access_token),

            "token_expires_in":
                long_lived_result.get(
                    "expires_in"
                )

        }


    # =========================================================
    # CONNECTION STATUS
    # =========================================================

    @classmethod
    def get_status(cls):

        try:

            access_token = (
                cls.get_access_token()
            )

            account_id = (
                cls.get_account_id()
            )

            username = session.get(
                "meta_username"
            )

            connected_session = (
                session.get(
                    "meta_connected",
                    False
                )
            )

            expires_in = (
                session.get(
                    "meta_token_expires_in"
                )
            )


            print(
                "================================"
            )

            print(
                "META STATUS CHECK"
            )

            print(
                "Access token tersedia:",
                bool(access_token)
            )

            print(
                "Account ID:",
                account_id
            )

            print(
                "Username:",
                username
            )

            print(
                "Connected session:",
                connected_session
            )

            print(
                "================================"
            )


            # -------------------------------------------------
            # TIDAK ADA TOKEN
            # -------------------------------------------------

            if not access_token:

                return {

                    "connected":
                        False,

                    "account_id":
                        None,

                    "username":
                        None,

                    "account":
                        None,

                    "token_received":
                        False,

                    "token_valid":
                        False,

                }


            # -------------------------------------------------
            # VALIDASI TOKEN
            # -------------------------------------------------

            try:

                account = (
                    cls.get_account_info(
                        access_token
                    )
                )


            except Exception as e:

                error_text = (
                    str(e).lower()
                )


                print(
                    "Gagal validasi token Instagram:",
                    repr(e)
                )


                # =================================================
                # ERROR SEMENTARA
                # =================================================

                temporary_error_keywords = [

                    "timeout",

                    "timed out",

                    "readtimeout",

                    "connection",

                    "connectionerror",

                    "connection aborted",

                    "max retries",

                    "temporary",

                    "502",

                    "503",

                    "504",

                    "429"

                ]


                is_temporary_error = any(

                    keyword in error_text

                    for keyword
                    in temporary_error_keywords

                )


                # =================================================
                # ERROR TOKEN INVALID
                # =================================================

                invalid_token_keywords = [

                    "invalid oauth",

                    "invalid access token",

                    "access token has expired",

                    "expired",

                    "oauth exception",

                    "oauthaccess",

                    "token has been invalidated",

                    "session has been invalidated"

                ]


                is_invalid_token = any(

                    keyword in error_text

                    for keyword
                    in invalid_token_keywords

                )


                # =================================================
                # TOKEN BENAR-BENAR INVALID
                # =================================================

                if is_invalid_token:

                    print(
                        "TOKEN INSTAGRAM BENAR-BENAR INVALID."
                    )


                    session[
                        "meta_connected"
                    ] = False

                    session.modified = True


                    return {

                        "connected":
                            False,

                        "account_id":
                            account_id,

                        "username":
                            username,

                        "account":
                            None,

                        "token_received":
                            True,

                        "token_valid":
                            False,

                        "temporary_error":
                            False,

                        "error":
                            str(e)

                    }


                # =================================================
                # ERROR SEMENTARA / TIDAK DIKENAL
                # =================================================
                #
                # Selama token masih ada, jangan ubah status
                # menjadi disconnected.
                #
                # =================================================

                if is_temporary_error:

                    print(
                        "API Instagram mengalami "
                        "gangguan sementara."
                    )

                else:

                    print(
                        "Error validasi belum dapat "
                        "dipastikan sebagai token invalid."
                    )


                print(
                    "Status koneksi dipertahankan."
                )


                session[
                    "meta_connected"
                ] = True

                session.modified = True


                return {

                    "connected":
                        True,

                    "account_id":
                        account_id,

                    "username":
                        username,

                    "account":
                        None,

                    "token_received":
                        True,

                    "token_valid":
                        None,

                    "temporary_error":
                        True,

                    "message":
                        (
                            "Token Instagram masih tersimpan. "
                            "Status koneksi dipertahankan."
                        )

                }


            # -------------------------------------------------
            # ACCOUNT BERHASIL
            # -------------------------------------------------

            real_account_id = (

                account.get(
                    "user_id"
                )

                or

                account.get(
                    "id"
                )

                or

                account_id

            )


            real_username = (

                account.get(
                    "username"
                )

                or

                username

            )


            # -------------------------------------------------
            # UPDATE SESSION
            # -------------------------------------------------

            session[
                "meta_account_id"
            ] = real_account_id

            session[
                "meta_username"
            ] = real_username

            session[
                "meta_connected"
            ] = True

            session.modified = True


            # -------------------------------------------------
            # RETURN CONNECTED
            # -------------------------------------------------

            return {

                "connected":
                    True,

                "account_id":
                    real_account_id,

                "username":
                    real_username,

                "account":
                    account,

                "token_received":
                    True,

                "token_valid":
                    True,

                "temporary_error":
                    False,

                "token_expires_in":
                    expires_in

            }


        except Exception as e:

            print(
                "ERROR get_status():",
                repr(e)
            )


            # =================================================
            # FALLBACK
            # =================================================
            #
            # Jika masih ada token, jangan membuat UI
            # terlihat disconnected hanya karena error internal.
            #
            # =================================================

            access_token = (
                cls.get_access_token()
            )

            account_id = (
                cls.get_account_id()
            )

            username = session.get(
                "meta_username"
            )


            if access_token:

                session[
                    "meta_connected"
                ] = True

                session.modified = True


                return {

                    "connected":
                        True,

                    "account_id":
                        account_id,

                    "username":
                        username,

                    "account":
                        None,

                    "token_received":
                        True,

                    "token_valid":
                        None,

                    "temporary_error":
                        True,

                    "message":
                        (
                            "Koneksi Instagram masih tersimpan, "
                            "tetapi status belum dapat divalidasi."
                        )

                }


            return {

                "connected":
                    False,

                "account_id":
                    None,

                "username":
                    None,

                "account":
                    None,

                "token_received":
                    False,

                "token_valid":
                    False

            }


    # =========================================================
    # HELPER: PARSE DATETIME
    # =========================================================

    @staticmethod
    def _parse_datetime(value):

        if not value:

            return datetime.utcnow()

        try:

            value = str(
                value
            ).replace(
                "Z",
                "+00:00"
            )

            return (
                datetime.fromisoformat(
                    value
                )
                .replace(
                    tzinfo=None
                )
            )

        except Exception:

            return datetime.utcnow()


    # =========================================================
    # HELPER: SAFE INTEGER
    # =========================================================

    @staticmethod
    def _int_value(value):

        try:

            if value is None:

                return 0

            return int(
                float(value)
            )

        except Exception:

            return 0


    # =========================================================
    # GET POST INSIGHTS
    # =========================================================

    @classmethod
    def get_media_insights(
        cls,
        media_id,
        access_token
    ):

        if not media_id:

            return {}

        url = (
            "https://graph.instagram.com/"
            f"v26.0/{media_id}/insights"
        )


        metric_sets = [

            [
                "views",
                "reach",
                "likes",
                "comments",
                "shares",
                "saved",
                "total_interactions"
            ],

            [
                "impressions",
                "reach",
                "likes",
                "comments",
                "shares",
                "saved"
            ],

            [
                "views",
                "reach"
            ]

        ]


        for metrics in metric_sets:

            try:

                response = requests.get(

                    url,

                    params={

                        "metric":
                            ",".join(
                                metrics
                            ),

                        "access_token":
                            access_token

                    },

                    timeout=30

                )


                if not response.ok:

                    continue


                result = (
                    response.json()
                )


                parsed = {}


                for item in result.get(
                    "data",
                    []
                ):

                    name = item.get(
                        "name"
                    )

                    values = item.get(
                        "values"
                    )


                    if (
                        name
                        and values
                    ):

                        last_value = (
                            values[-1].get(
                                "value"
                            )
                        )

                        parsed[name] = (
                            cls._int_value(
                                last_value
                            )
                        )


                    elif name:

                        parsed[name] = (
                            cls._int_value(
                                item.get(
                                    "value"
                                )
                            )
                        )


                if parsed:

                    return parsed


            except Exception as e:

                print(
                    "Gagal mengambil insight media",
                    media_id,
                    ":",
                    repr(e)
                )


        return {}


    # =========================================================
    # GET ACCOUNT INSIGHTS
    # =========================================================

    @classmethod
    def get_account_insights(
        cls,
        account_id,
        access_token
    ):
        """
        Ambil Account Insights Instagram.

        Metric account yang digunakan:
        - accounts_reached
        - accounts_engaged
        - profile_views
        - website_clicks
        - profile_links_taps

        profile_views dari Meta dipetakan ke field aplikasi
        profile_views agar kompatibel dengan database/dashboard lama.

        Request profile_views dicoba menggunakan format Account Insights
        yang didokumentasikan Meta (period=day). Jika request tersebut
        gagal dan API memberi indikasi kebutuhan metric_type, dilakukan
        satu fallback menggunakan metric_type=total_value.

        Tidak ada nilai metric yang gagal dipaksa menjadi 0 tanpa
        informasi error. Error disimpan pada _errors.
        """
        if not account_id or not access_token:
            return {}

        url = (
            "https://graph.instagram.com/"
            f"v26.0/{account_id}/insights"
        )

        metric_candidates = [
            "accounts_reached",
            "accounts_engaged",
            "profile_views",
            "website_clicks",
            "profile_links_taps",
        ]

        parsed = {}
        errors = {}

        def parse_metric_result(
            metric_name,
            result
        ):
            """
            Ambil nilai metric dari beberapa bentuk response Meta.
            Prioritas:
            1. total_value.value
            2. values[-1].value
            3. value
            """
            data_items = result.get("data") or []

            target = None

            for item in data_items:
                if item.get("name") == metric_name:
                    target = item
                    break

            if target is None:
                return None

            total_value = target.get("total_value")

            if isinstance(total_value, dict):
                if "value" in total_value:
                    return cls._int_value(
                        total_value.get("value")
                    )

            values = target.get("values") or []

            if values:
                # Untuk profile_views dashboard, gunakan nilai
                # observasi terbaru agar tidak berubah menjadi
                # akumulasi lintas hari.
                latest = values[-1]

                if isinstance(latest, dict):
                    return cls._int_value(
                        latest.get("value")
                    )

                return cls._int_value(latest)

            if "value" in target:
                return cls._int_value(
                    target.get("value")
                )

            return None

        for metric_name in metric_candidates:
            try:
                response = requests.get(
                    url,
                    params={
                        "metric": metric_name,
                        "period": "day",
                        "access_token": access_token
                    },
                    timeout=20
                )

                try:
                    body = response.json()
                except Exception:
                    body = None

                if response.ok:
                    value = parse_metric_result(
                        metric_name,
                        body or {}
                    )

                    if value is not None:
                        parsed[metric_name] = value
                        continue

                    # SATU PERBAIKAN:
                    # Meta dapat mengembalikan HTTP 200 dengan data=[].
                    # Untuk profile_views, tetap jalankan fallback yang
                    # sebelumnya berhasil menghasilkan nilai 2.
                    if metric_name == "profile_views":
                        try:
                            print(
                                "PROFILE_VIEWS EMPTY - TRY metric_type=total_value"
                            )

                            fallback_response = requests.get(
                                url,
                                params={
                                    "metric": "profile_views",
                                    "metric_type": "total_value",
                                    "period": "day",
                                    "access_token": access_token
                                },
                                timeout=20
                            )

                            try:
                                fallback_body = (
                                    fallback_response.json()
                                )
                            except Exception:
                                fallback_body = None

                            print(
                                "PROFILE_VIEWS FALLBACK HTTP:",
                                fallback_response.status_code
                            )

                            if fallback_response.ok:
                                fallback_value = parse_metric_result(
                                    "profile_views",
                                    fallback_body or {}
                                )

                                if fallback_value is not None:
                                    parsed["profile_views"] = fallback_value
                                    print(
                                        "PROFILE_VIEWS FALLBACK VALUE:",
                                        fallback_value
                                    )
                                    continue

                            errors[metric_name] = {
                                "status": fallback_response.status_code,
                                "response":
                                    fallback_body
                                    if fallback_body is not None
                                    else fallback_response.text[:1000],
                                "initial_status":
                                    response.status_code,
                                "initial_response":
                                    body
                                    if body is not None
                                    else response.text[:1000]
                            }

                        except Exception as fallback_error:
                            errors[metric_name] = {
                                "status": response.status_code,
                                "response":
                                    body
                                    if body is not None
                                    else response.text[:1000],
                                "fallback_error":
                                    repr(fallback_error)
                            }

                        continue

                    errors[metric_name] = {
                        "status": response.status_code,
                        "response": body
                        if body is not None
                        else response.text[:1000],
                        "message":
                            "Metric tidak ditemukan pada response API."
                    }

                    continue

                # Fallback khusus profile_views.
                # Request standar dicoba terlebih dahulu. Fallback hanya
                # dipakai jika request pertama gagal.
                if metric_name == "profile_views":
                    try:
                        fallback_response = requests.get(
                            url,
                            params={
                                "metric": "profile_views",
                                "metric_type": "total_value",
                                "period": "day",
                                "access_token": access_token
                            },
                            timeout=20
                        )

                        try:
                            fallback_body = (
                                fallback_response.json()
                            )
                        except Exception:
                            fallback_body = None

                        if fallback_response.ok:
                            fallback_value = parse_metric_result(
                                "profile_views",
                                fallback_body or {}
                            )

                            if fallback_value is not None:
                                parsed[
                                    "profile_views"
                                ] = fallback_value
                                continue

                        errors[metric_name] = {
                            "status": fallback_response.status_code,
                            "response":
                                fallback_body
                                if fallback_body is not None
                                else fallback_response.text[:1000],
                            "initial_status":
                                response.status_code,
                            "initial_response":
                                body
                                if body is not None
                                else response.text[:1000]
                        }

                    except Exception as fallback_error:
                        errors[metric_name] = {
                            "status": response.status_code,
                            "response":
                                body
                                if body is not None
                                else response.text[:1000],
                            "fallback_error":
                                repr(fallback_error)
                        }

                    continue

                errors[metric_name] = {
                    "status": response.status_code,
                    "response":
                        body
                        if body is not None
                        else response.text[:1000]
                }

            except Exception as e:
                errors[metric_name] = repr(e)

        # Mapping Meta -> database/dashboard.
        if "profile_views" in parsed:
            parsed["profile_views"] = parsed[
                "profile_views"
            ]

        # Jangan menyamakan profile_links_taps dengan profile_views.
        if "profile_links_taps" in parsed:
            parsed["profile_links_taps"] = parsed[
                "profile_links_taps"
            ]

        if errors:
            parsed["_errors"] = errors

        return parsed


    # =========================================================
    # SAVE / UPDATE POST
    # =========================================================

    @classmethod
    def save_post(
        cls,
        media,
        access_token
    ):

        meta_post_id = (
            media.get(
                "id"
            )
        )


        if not meta_post_id:

            return None


        post = (
            Posts.query
            .filter_by(
                meta_post_id=
                    meta_post_id
            )
            .first()
        )


        posted_at = (
            cls._parse_datetime(
                media.get(
                    "timestamp"
                )
            )
        )


        if post is None:

            post = Posts(

                meta_post_id=
                    meta_post_id,

                caption=
                    media.get(
                        "caption"
                    ),

                media_type=
                    media.get(
                        "media_type"
                    ),

                media_product_type=
                    media.get(
                        "media_product_type"
                    ),

                collaboration=
                    media.get(
                        "collaboration"
                    ),

                posted_at=
                    posted_at,

                created_at=
                    datetime.utcnow()

            )


            db.session.add(
                post
            )

            db.session.flush()


        else:

            post.caption = (
                media.get(
                    "caption"
                )
            )

            post.media_type = (
                media.get(
                    "media_type"
                )
            )

            post.media_product_type = (
                media.get(
                    "media_product_type"
                )
            )

            post.collaboration = (
                media.get(
                    "collaboration"
                )
            )

            post.posted_at = (
                posted_at
            )


        # -----------------------------------------------------
        # AMBIL INSIGHT
        # -----------------------------------------------------

        insights = (
            cls.get_media_insights(
                meta_post_id,
                access_token
            )
        )


        likes = cls._int_value(

            insights.get(
                "likes",
                media.get(
                    "like_count",
                    0
                )
            )

        )


        comments = cls._int_value(

            insights.get(
                "comments",
                media.get(
                    "comments_count",
                    0
                )
            )

        )


        views = cls._int_value(

            insights.get(
                "views",
                media.get(
                    "views",
                    0
                )
            )

        )


        reach = cls._int_value(

            insights.get(
                "reach",
                0
            )

        )


        impressions = cls._int_value(

            insights.get(
                "impressions",
                0
            )

        )


        shares = cls._int_value(

            insights.get(
                "shares",
                0
            )

        )


        saves = cls._int_value(

            insights.get(
                "saved",
                insights.get(
                    "saves",
                    0
                )
            )

        )


        content_interactions = (
            cls._int_value(

                insights.get(

                    "total_interactions",

                    likes
                    + comments
                    + shares
                    + saves

                )

            )
        )


        accounts_engaged = (
            cls._int_value(

                insights.get(
                    "accounts_engaged",
                    0
                )

            )
        )


        denominator = (

            reach

            if reach > 0

            else views

        )


        engagement_rate = 0.0


        if denominator > 0:

            engagement_rate = (

                (

                    likes
                    + comments
                    + shares
                    + saves

                )

                / denominator

            ) * 100


        # -----------------------------------------------------
        # UPDATE METRIC TERBARU
        # -----------------------------------------------------

        metric = (

            Post_Metrics.query

            .filter_by(
                id_posts=
                    post.id_posts
            )

            .order_by(
                Post_Metrics.metric_date.desc()
            )

            .first()

        )


        if metric is None:

            metric = Post_Metrics(

                id_posts=
                    post.id_posts,

                metric_date=
                    datetime.utcnow()

            )

            db.session.add(
                metric
            )


        metric.views = views

        metric.reach = reach

        metric.impressions = (
            impressions
        )

        metric.likes = likes

        metric.comments = comments

        metric.shares = shares

        metric.saves = saves

        metric.accounts_engaged = (
            accounts_engaged
        )

        metric.content_interactions = (
            content_interactions
        )

        metric.engagement_rate = (
            engagement_rate
        )

        metric.metric_date = (
            datetime.utcnow()
        )


        return post


    # =========================================================
    # SAVE ACCOUNT METRICS
    # =========================================================

    @classmethod
    def save_account_metrics(
        cls,
        account,
        insights
    ):
        """
        Simpan account metrics harian. Record pada tanggal yang sama
        di-update agar sync berulang tidak membuat duplikasi.
        """
        account = account or {}
        insights = insights or {}

        followers = cls._int_value(
            account.get("followers_count", 0)
        )

        accounts_reached = cls._int_value(
            insights.get("accounts_reached", 0)
        )

        accounts_engaged = cls._int_value(
            insights.get("accounts_engaged", 0)
        )

        profile_views = cls._int_value(
            insights.get(
                "profile_views",
                insights.get("profile_views", 0)
            )
        )

        website_clicks = cls._int_value(
            insights.get(
                "website_clicks",
                insights.get("profile_links_taps", 0)
            )
        )

        now = datetime.utcnow()
        metric_date = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        # Simpan setiap hasil sinkronisasi sebagai snapshot histori.
        # Tidak lagi menimpa record pada tanggal yang sama, sehingga
        # setiap Sync tetap tersimpan dan dapat ditelusuri.
        metric = Account_Metrics(
            followers=followers,
            accounts_reached=accounts_reached,
            accounts_engaged=accounts_engaged,
            profile_views=profile_views,
            website_clicks=website_clicks,
            metric_date=now
        )

        db.session.add(metric)
        return metric


    # =========================================================
    # SYNCHRONIZE
    # =========================================================

    @classmethod
    def synchronize(cls):

        sync_log = SyncLog(

            sync_date=
                datetime.utcnow(),

            total_posts=
                0,

            status=
                "PROCESSING",

            message=
                "Sinkronisasi Instagram sedang diproses."

        )


        db.session.add(
            sync_log
        )


        try:

            # -------------------------------------------------
            # TOKEN
            # -------------------------------------------------

            access_token = (
                cls.get_access_token()
            )


            if not access_token:

                raise ValueError(
                    "Instagram belum terhubung. "
                    "Access token tidak ditemukan."
                )


            # -------------------------------------------------
            # ACCOUNT
            # -------------------------------------------------

            account = (
                cls.get_account_info(
                    access_token
                )
            )


            account_id = (

                account.get(
                    "user_id"
                )

                or

                account.get(
                    "id"
                )

                or

                cls.get_account_id()

            )


            if not account_id:

                raise ValueError(
                    "Instagram Account ID tidak ditemukan."
                )


            session[
                "meta_account_id"
            ] = account_id


            session[
                "meta_username"
            ] = account.get(
                "username"
            )


            session[
                "meta_connected"
            ] = True


            session.modified = True


            # -------------------------------------------------
            
            # -----------------------------------------------------
            # HAPUS POST LAMA SEBELUM SINKRONISASI
            # -----------------------------------------------------
            #
            # Posts tidak mempunyai account_id pada ERD, sehingga
            # data post lama tidak dapat dipisahkan berdasarkan akun.
            # Karena itu seluruh data Posts beserta data turunannya
            # dibersihkan sebelum mengambil data Instagram terbaru.
            #
            # Tabel anak dihapus lebih dahulu untuk menghindari
            # foreign-key constraint.
            # -----------------------------------------------------

            print("")
            print("====================================")
            print("RESET DATA POST LAMA")
            print("Menghapus data sinkronisasi sebelumnya...")

            old_metrics = db.session.query(
                Post_Metrics
            ).delete(
                synchronize_session=False
            )

            old_clusters = db.session.query(
                Clusters
            ).delete(
                synchronize_session=False
            )

            old_forecasts = db.session.query(
                Forecast
            ).delete(
                synchronize_session=False
            )

            old_posts = db.session.query(
                Posts
            ).delete(
                synchronize_session=False
            )

            db.session.commit()

            print(
                "Post lama dihapus:",
                old_posts
            )

            print(
                "Metric post lama dihapus:",
                old_metrics
            )

            print(
                "Cluster lama dihapus:",
                old_clusters
            )

            print(
                "Forecast lama dihapus:",
                old_forecasts
            )

            print("RESET DATA POST SELESAI")
            print("====================================")


# MEDIA
            # -------------------------------------------------

            media_result = (
                cls.get_media(

                    account_id=
                        account_id,

                    access_token=
                        access_token,

                    limit=
                        100

                )
            )


            media_items = (
                media_result.get(
                    "data",
                    []
                )
            )


            print("")

            print(
                "===================================="
            )

            print(
                "INSTAGRAM SYNCHRONIZATION"
            )

            print(
                "ACCOUNT:",
                account.get(
                    "username"
                )
            )

            print(
                "ACCOUNT ID:",
                account_id
            )

            print(
                "TOTAL MEDIA:",
                len(media_items)
            )

            print(
                "===================================="
            )


            # -------------------------------------------------
            # SAVE POSTS + METRICS
            # -------------------------------------------------

            saved_posts = 0

            failed_posts = 0

            # Satu media diproses dalam transaksi terpisah.
            # Jika MySQL mengembalikan error 1205 (lock wait timeout),
            # media tersebut otomatis dicoba kembali maksimal 3 kali.
            max_retries = 3

            for media in media_items:

                media_id = media.get("id")
                saved_this_media = False

                for attempt in range(1, max_retries + 1):

                    try:

                        post = cls.save_post(
                            media,
                            access_token
                        )

                        if not post:
                            raise RuntimeError(
                                "Media tidak dapat disimpan."
                            )

                        # Commit langsung setelah satu media berhasil.
                        # Ini mencegah satu transaksi besar menahan lock
                        # selama seluruh 193 media diproses.
                        db.session.commit()

                        saved_posts += 1
                        saved_this_media = True

                        break

                    except Exception as e:

                        db.session.rollback()

                        error_text = str(e).lower()

                        is_lock_timeout = (
                            "1205" in error_text
                            or
                            "lock wait timeout" in error_text
                        )

                        if (
                            is_lock_timeout
                            and attempt < max_retries
                        ):

                            wait_seconds = attempt * 2

                            print(
                                f"Lock database pada media "
                                f"{media_id}. "
                                f"Retry {attempt}/{max_retries - 1} "
                                f"dalam {wait_seconds} detik..."
                            )

                            time.sleep(wait_seconds)

                            continue

                        print(
                            "Gagal menyimpan media",
                            media_id,
                            ":",
                            repr(e)
                        )

                        break

                if not saved_this_media:
                    failed_posts += 1

                # Jeda kecil untuk mengurangi lock contention.
                time.sleep(0.05)

            # -----------------------------------------------------
            # ACCOUNT INSIGHTS
            # -----------------------------------------------------

            # -------------------------------------------------

            account_insights = (
                cls.get_account_insights(

                    account_id=
                        account_id,

                    access_token=
                        access_token

                )
            )


            account_metric = cls.save_account_metrics(
                account,
                account_insights
            )

            # Commit account metric terlebih dahulu. Dengan begitu,
            # kegagalan AI analysis tidak menghapus hasil sinkronisasi
            # account metrics.
            db.session.commit()

            # -------------------------------------------------
            # AI ANALYSIS
            # -------------------------------------------------
            # Import lokal untuk menghindari circular import.
            # Analisis dijalankan setelah Posts + Post_Metrics selesai
            # disimpan, sehingga Cluster dan Forecast dapat langsung
            # dibuat dalam database.
            ai_analysis = None
            ai_analysis_error = None

            try:
                from services.ai_analysis_service import AIAnalysisService

                ai_analysis = AIAnalysisService.analyze()

            except Exception as analysis_error:
                db.session.rollback()
                ai_analysis_error = repr(analysis_error)
                print(
                    "AI analysis setelah sync gagal:",
                    ai_analysis_error
                )

            # -------------------------------------------------
            # SYNC LOG
            # -------------------------------------------------

            sync_log.total_posts = (
                saved_posts
            )


            if failed_posts > 0:

                sync_log.status = (
                    "PARTIAL"
                )


                sync_log.message = (

                    f"Sinkronisasi selesai. "

                    f"{saved_posts} media berhasil "
                    f"disimpan, "

                    f"{failed_posts} media gagal."

                )


            else:

                sync_log.status = (
                    "SUCCESS"
                )


                sync_log.message = (

                    f"Sinkronisasi berhasil. "

                    f"{saved_posts} media Instagram "
                    f"berhasil disimpan."

                )


            sync_log.sync_date = (
                datetime.utcnow()
            )


            db.session.commit()


            print(

                "SINKRONISASI BERHASIL:",

                saved_posts,

                "posts"

            )


            ai_analysis_summary = {
                "success": ai_analysis is not None,
                "total_content": (
                    ai_analysis.get("total_content", 0)
                    if isinstance(ai_analysis, dict)
                    else 0
                ),
                "forecast_count": (
                    len(ai_analysis.get("forecast", []))
                    if isinstance(ai_analysis, dict)
                    and isinstance(ai_analysis.get("forecast"), list)
                    else 0
                ),
                "cluster_save": (
                    ai_analysis.get("cluster_save")
                    if isinstance(ai_analysis, dict)
                    else None
                ),
                "forecast_save": (
                    ai_analysis.get("forecast_save")
                    if isinstance(ai_analysis, dict)
                    else None
                ),
                "error": ai_analysis_error
            }

            return {

                "success":
                    True,

                "connected":
                    True,

                "account":
                    account,

                "account_insights":
                    account_insights,

                "account_metric": {
                    "id_am": getattr(account_metric, "id_am", None),
                    "followers": getattr(account_metric, "followers", 0),
                    "accounts_reached": getattr(account_metric, "accounts_reached", 0),
                    "accounts_engaged": getattr(account_metric, "accounts_engaged", 0),
                    "profile_views": getattr(account_metric, "profile_views", 0),
                    "website_clicks": getattr(account_metric, "website_clicks", 0),
                    "metric_date": (
                        account_metric.metric_date.isoformat()
                        if getattr(account_metric, "metric_date", None)
                        else None
                    )
                },

                "ai_analysis":
                    ai_analysis,

                "ai_analysis_summary":
                    ai_analysis_summary,

                "ai_analysis_error":
                    ai_analysis_error,

                "total_media":
                    len(media_items),

                "saved_posts":
                    saved_posts,

                "failed_posts":
                    failed_posts,

                "message":
                    sync_log.message

            }


        except Exception as e:

            print("")

            print(
                "===================================="
            )

            print(
                "SINKRONISASI INSTAGRAM GAGAL"
            )

            print(
                repr(e)
            )

            print(
                "===================================="
            )


            db.session.rollback()


            try:

                failed_log = SyncLog(

                    sync_date=
                        datetime.utcnow(),

                    total_posts=
                        0,

                    status=
                        "FAILED",

                    message=
                        str(e)

                )


                db.session.add(
                    failed_log
                )


                db.session.commit()


            except Exception:

                db.session.rollback()


            raise