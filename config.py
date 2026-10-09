import os
from datetime import timedelta

from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


class Config:

    # =========================================================
    # DATABASE
    # =========================================================

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://"
        f"{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # =========================================================
    # FLASK
    # =========================================================

    SECRET_KEY = os.getenv(
        "SECRET_KEY"
    )


    # =========================================================
    # JWT
    # =========================================================

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY"
    )

    # JWT login berlaku 8 jam
    # sehingga tidak expired saat proses sinkronisasi
    # Instagram/Meta berlangsung lama.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=8
    )


    # =========================================================
    # META / INSTAGRAM LOGIN
    # =========================================================

    META_APP_ID = os.getenv(
        "META_APP_ID"
    )

    META_APP_SECRET = os.getenv(
        "META_APP_SECRET"
    )

    META_ACCESS_TOKEN = os.getenv(
        "META_ACCESS_TOKEN"
    )

    META_ACCOUNT_ID = os.getenv(
        "META_ACCOUNT_ID"
    )

    META_REDIRECT_URI = os.getenv(
        "META_REDIRECT_URI"
    )

    META_OAUTH_URL = (
        os.getenv("META_OAUTH_URL")
        or "https://www.instagram.com/oauth/authorize"
    )

    META_TOKEN_URL = (
        os.getenv("META_TOKEN_URL")
        or "https://api.instagram.com/oauth/access_token"
    )

    META_TOKEN_EXCHANGE_URL = (
        "https://graph.instagram.com/access_token"
    )

    META_GRAPH_URL = (
        "https://graph.instagram.com"
    )


    # =========================================================
    # FACEBOOK LOGIN
    # =========================================================

    # Configuration ID dari Facebook Login for Business
    FB_CONFIG_ID = os.getenv(
        "FB_CONFIG_ID"
    )

    # Callback Facebook
    FB_REDIRECT_URI = os.getenv(
        "FB_REDIRECT_URI"
    )

    # URL OAuth Facebook
    FB_OAUTH_URL = (
        os.getenv("FB_OAUTH_URL")
        or "https://www.facebook.com/v26.0/dialog/oauth"
    )

    # URL pertukaran authorization code ke access token
    FB_TOKEN_URL = (
        os.getenv("FB_TOKEN_URL")
        or "https://graph.facebook.com/v26.0/oauth/access_token"
    )

    # Graph API Facebook
    FB_GRAPH_URL = (
        os.getenv("FB_GRAPH_URL")
        or "https://graph.facebook.com/v26.0"
    )


    # =========================================================
    # GEMINI
    # =========================================================

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY"
    )