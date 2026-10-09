import os
import requests

from dotenv import load_dotenv


load_dotenv()


class MetaAPI:

    BASE_URL = "https://graph.facebook.com"

    @staticmethod
    def get_access_token():
        return os.getenv("META_ACCESS_TOKEN")

    @staticmethod
    def get_account_id():
        return os.getenv("META_ACCOUNT_ID")

    @staticmethod
    def get_api_version():
        return os.getenv(
            "META_API_VERSION",
            "v23.0"
        )

    @classmethod
    def request(
        cls,
        endpoint,
        params=None
    ):

        access_token = cls.get_access_token()

        if not access_token:
            raise ValueError(
                "META_ACCESS_TOKEN belum dikonfigurasi"
            )

        version = cls.get_api_version()

        url = (
            f"{cls.BASE_URL}/"
            f"{version}/"
            f"{endpoint}"
        )

        request_params = params or {}

        request_params["access_token"] = access_token

        response = requests.get(
            url,
            params=request_params,
            timeout=30
        )

        if not response.ok:

            try:
                error_data = response.json()
            except Exception:
                error_data = {
                    "message": response.text
                }

            raise Exception(
                f"Meta API error: {error_data}"
            )

        return response.json()