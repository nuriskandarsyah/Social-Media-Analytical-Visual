# services/facebook_service.py

import json
import os
from datetime import datetime, timedelta, timezone

import requests

from extensions import db

from models import (
    Facebook_Connections,
    Facebook_Insights,
    Facebook_Contents
)


class FacebookService:

    # =========================================================
    # CONFIG
    # =========================================================

    GRAPH_URL = (
        os.getenv("FB_GRAPH_URL")
        or "https://graph.facebook.com/v26.0"
    ).rstrip("/")

    DEFAULT_INSIGHT_METRICS = (
        "page_post_engagements,"
        "page_views_total,"
        "page_media_view"
    )

    DEFAULT_INSIGHT_PERIOD = "days_28"

    DEFAULT_CONTENT_LIMIT = 25

    # =========================================================
    # BASIC HELPERS
    # =========================================================

    @staticmethod
    def _safe_int(value):
        try:
            return int(float(value or 0))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _safe_float(value):
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _parse_datetime(value):
        if not value:
            return None

        if isinstance(value, datetime):
            dt = value

        else:
            try:
                text = str(value).strip()

                if text.endswith("Z"):
                    text = text[:-1] + "+00:00"

                dt = datetime.fromisoformat(text)

            except (TypeError, ValueError):
                return None

        try:
            if dt.tzinfo is not None:
                dt = dt.astimezone().replace(
                    tzinfo=None
                )
        except Exception:
            pass

        return dt

    @classmethod
    def _request_get(
        cls,
        path,
        access_token,
        params=None
    ):
        if not access_token:
            raise ValueError(
                "Access token Facebook tidak tersedia."
            )

        request_params = dict(
            params or {}
        )

        request_params["access_token"] = (
            access_token
        )

        url = (
            f"{cls.GRAPH_URL}"
            f"{path}"
        )

        try:

            response = requests.get(
                url,
                params=request_params,
                timeout=30
            )

        except requests.exceptions.RequestException as e:

            raise RuntimeError(
                "Gagal mengakses Facebook Graph API: "
                f"{e}"
            ) from e

        try:
            result = response.json()

        except Exception:
            result = {
                "raw_response": response.text
            }

        if not response.ok:

            error = result.get(
                "error",
                {}
            )

            if isinstance(
                error,
                dict
            ):

                message = (
                    error.get("message")
                    or str(error)
                )

            else:

                message = str(error)

            raise RuntimeError(
                "Facebook Graph API error "
                f"(HTTP {response.status_code}): "
                f"{message}"
            )

        return result

    # =========================================================
    # GET TOKEN
    # =========================================================

    @classmethod
    def get_access_token(
        cls,
        connection
    ):
        if not connection:
            return None

        return (
            getattr(
                connection,
                "page_access_token",
                None
            )
        )

    # =========================================================
    # GET CONNECTIONS
    # =========================================================

    @classmethod
    def get_connections(
        cls,
        mavis_user_id
    ):

        connections = (
            Facebook_Connections.query
            .filter_by(
                mavis_user_id=int(
                    mavis_user_id
                ),
                connected=True
            )
            .order_by(
                Facebook_Connections.updated_at.desc()
            )
            .all()
        )

        return [
            cls._serialize_connection(
                connection
            )
            for connection in connections
        ]

    @classmethod
    def get_connection(
        cls,
        mavis_user_id,
        page_id=None
    ):

        query = (
            Facebook_Connections.query
            .filter_by(
                mavis_user_id=int(
                    mavis_user_id
                ),
                connected=True
            )
        )

        if page_id:

            query = query.filter_by(
                page_id=str(
                    page_id
                )
            )

        connection = (
            query
            .order_by(
                Facebook_Connections.updated_at.desc()
            )
            .first()
        )

        return connection

    @classmethod
    def get_status(
        cls,
        mavis_user_id
    ):

        connections = (
            Facebook_Connections.query
            .filter_by(
                mavis_user_id=int(
                    mavis_user_id
                ),
                connected=True
            )
            .order_by(
                Facebook_Connections.updated_at.desc()
            )
            .all()
        )

        if not connections:

            return {
                "connected": False,
                "facebook_user_id": None,
                "facebook_user_name": None,
                "pages": []
            }

        first = connections[0]

        return {
            "connected": True,
            "facebook_user_id": (
                first.facebook_user_id
            ),
            "facebook_user_name": (
                first.facebook_user_name
            ),
            "expires_in": (
                first.expires_in
            ),
            "expires_at": (
                first.expires_at.isoformat()
                if first.expires_at
                else None
            ),
            "pages": [
                {
                    "id": connection.page_id,
                    "name": connection.page_name,
                    "category": connection.page_category
                }
                for connection in connections
            ]
        }

    @classmethod
    def get_pages_from_database(
        cls,
        mavis_user_id
    ):

        connections = (
            Facebook_Connections.query
            .filter_by(
                mavis_user_id=int(
                    mavis_user_id
                ),
                connected=True
            )
            .order_by(
                Facebook_Connections.page_name.asc()
            )
            .all()
        )

        return [
            {
                "id": connection.page_id,
                "name": connection.page_name,
                "category": connection.page_category
            }
            for connection in connections
        ]

    @classmethod
    def select_page(
        cls,
        mavis_user_id,
        page_id
    ):

        connection = (
            cls.get_connection(
                mavis_user_id=mavis_user_id,
                page_id=page_id
            )
        )

        if not connection:
            raise ValueError(
                "Facebook Page tidak ditemukan."
            )

        return {
            "id": connection.page_id,
            "name": connection.page_name,
            "category": connection.page_category
        }

    # =========================================================
    # SERIALIZE CONNECTION
    # =========================================================

    @staticmethod
    def _serialize_connection(
        connection
    ):

        return {
            "id": connection.id,
            "mavis_user_id": (
                connection.mavis_user_id
            ),
            "facebook_user_id": (
                connection.facebook_user_id
            ),
            "facebook_user_name": (
                connection.facebook_user_name
            ),
            "page_id": (
                connection.page_id
            ),
            "page_name": (
                connection.page_name
            ),
            "page_category": (
                connection.page_category
            ),
            "expires_in": (
                connection.expires_in
            ),
            "expires_at": (
                connection.expires_at.isoformat()
                if connection.expires_at
                else None
            ),
            "connected": (
                bool(connection.connected)
            ),
            "connected_at": (
                connection.connected_at.isoformat()
                if connection.connected_at
                else None
            ),
            "updated_at": (
                connection.updated_at.isoformat()
                if connection.updated_at
                else None
            )
        }

    # =========================================================
    # SAVE FACEBOOK CONNECTION
    # =========================================================

    @classmethod
    def save_connections(
        cls,
        mavis_user_id,
        facebook_user,
        pages,
        expires_in=None
    ):

        mavis_user_id = int(
            mavis_user_id
        )

        facebook_user_id = str(
            facebook_user.get("id")
            or ""
        ).strip()

        facebook_user_name = (
            facebook_user.get("name")
        )

        if not facebook_user_id:

            raise ValueError(
                "Facebook User ID tidak ditemukan."
            )

        saved = []

        expires_at = None

        if expires_in:

            try:

                expires_at = (
                    datetime.utcnow()
                    + timedelta(
                        seconds=int(
                            expires_in
                        )
                    )
                )

            except (
                TypeError,
                ValueError
            ):

                expires_at = None

        for page in pages or []:

            page_id = str(
                page.get("id")
                or ""
            ).strip()

            page_name = (
                page.get("name")
                or ""
            ).strip()

            if not page_id:
                continue

            connection = (
                Facebook_Connections.query
                .filter_by(
                    mavis_user_id=mavis_user_id,
                    facebook_user_id=facebook_user_id,
                    page_id=page_id
                )
                .first()
            )

            if connection:

                connection.facebook_user_name = (
                    facebook_user_name
                )

                connection.page_name = (
                    page_name
                )

                connection.page_category = (
                    page.get("category")
                )

                if page.get(
                    "access_token"
                ):

                    connection.page_access_token = (
                        page.get("access_token")
                    )

                connection.expires_in = (
                    expires_in
                )

                connection.expires_at = (
                    expires_at
                )

                connection.connected = True

            else:

                page_access_token = (
                    page.get("access_token")
                )

                if not page_access_token:

                    continue

                connection = Facebook_Connections(
                    mavis_user_id=mavis_user_id,
                    facebook_user_id=(
                        facebook_user_id
                    ),
                    facebook_user_name=(
                        facebook_user_name
                    ),
                    page_id=page_id,
                    page_name=page_name,
                    page_category=(
                        page.get("category")
                    ),
                    page_access_token=(
                        page_access_token
                    ),
                    expires_in=expires_in,
                    expires_at=expires_at,
                    connected=True
                )

                db.session.add(
                    connection
                )

            saved.append(
                connection
            )

        db.session.commit()

        return [
            cls._serialize_connection(
                item
            )
            for item in saved
        ]

    # =========================================================
    # FACEBOOK PAGE INFORMATION
    # =========================================================

    @classmethod
    def get_page_info(
        cls,
        mavis_user_id,
        page_id=None
    ):

        connection = (
            cls.get_connection(
                mavis_user_id,
                page_id
            )
        )

        if not connection:

            raise ValueError(
                "Facebook Page tidak ditemukan."
            )

        token = (
            cls.get_access_token(
                connection
            )
        )

        data = cls._request_get(
            f"/{connection.page_id}",
            token,
            {
                "fields": (
                    "id,name,category"
                )
            }
        )

        return data

    # =========================================================
    # FACEBOOK INSIGHTS
    # =========================================================

    @classmethod
    def fetch_insights(
        cls,
        mavis_user_id,
        page_id=None,
        metric=None,
        period=None,
        since=None,
        until=None
    ):

        connection = (
            cls.get_connection(
                mavis_user_id,
                page_id
            )
        )

        if not connection:

            raise ValueError(
                "Facebook Page belum terhubung."
            )

        token = (
            cls.get_access_token(
                connection
            )
        )

        metric = (
            metric
            or cls.DEFAULT_INSIGHT_METRICS
        )

        period = (
            period
            or cls.DEFAULT_INSIGHT_PERIOD
        )

        params = {
            "metric": metric,
            "period": period
        }

        if since:
            params["since"] = since

        if until:
            params["until"] = until

        data = cls._request_get(
            (
                f"/{connection.page_id}"
                "/insights"
            ),
            token,
            params
        )

        return {
            "page": {
                "id": connection.page_id,
                "name": connection.page_name
            },
            "data": (
                data.get(
                    "data",
                    []
                )
            ),
            "paging": (
                data.get(
                    "paging"
                )
            )
        }

    # =========================================================
    # SAVE INSIGHTS
    # =========================================================

    @classmethod
    def save_insights(
        cls,
        mavis_user_id,
        page_id,
        insights
    ):

        connection = (
            cls.get_connection(
                mavis_user_id,
                page_id
            )
        )

        if not connection:

            raise ValueError(
                "Facebook connection tidak ditemukan."
            )

        saved_count = 0

        for metric in insights or []:

            metric_name = (
                metric.get("name")
            )

            metric_title = (
                metric.get("title")
            )

            metric_description = (
                metric.get("description")
            )

            period = (
                metric.get("period")
                or ""
            )

            values = metric.get(
                "values",
                []
            )

            for item in values or []:

                value = item.get(
                    "value"
                )

                end_time = (
                    cls._parse_datetime(
                        item.get(
                            "end_time"
                        )
                    )
                )

                numeric_value = 0

                if isinstance(
                    value,
                    (int, float)
                ):

                    numeric_value = (
                        value
                    )

                elif isinstance(
                    value,
                    str
                ):

                    numeric_value = (
                        cls._safe_float(
                            value
                        )
                    )

                elif isinstance(
                    value,
                    dict
                ):

                    numeric_value = (
                        cls._safe_float(
                            value.get(
                                "value"
                            )
                        )
                    )

                existing = None

                query = (
                    Facebook_Insights.query
                    .filter_by(
                        connection_id=(
                            connection.id
                        ),
                        metric_name=(
                            metric_name
                        ),
                        period=period
                    )
                )

                if end_time is None:

                    existing = (
                        query
                        .filter(
                            Facebook_Insights.end_time.is_(None)
                        )
                        .first()
                    )

                else:

                    existing = (
                        query
                        .filter_by(
                            end_time=end_time
                        )
                        .first()
                    )

                if existing:

                    existing.metric_title = (
                        metric_title
                    )

                    existing.metric_description = (
                        metric_description
                    )

                    existing.metric_value = (
                        numeric_value
                    )

                    existing.page_name = (
                        connection.page_name
                    )

                else:

                    row = Facebook_Insights(
                        connection_id=(
                            connection.id
                        ),
                        mavis_user_id=(
                            int(mavis_user_id)
                        ),
                        page_id=(
                            connection.page_id
                        ),
                        page_name=(
                            connection.page_name
                        ),
                        metric_name=(
                            metric_name
                        ),
                        metric_title=(
                            metric_title
                        ),
                        metric_description=(
                            metric_description
                        ),
                        period=(
                            period
                        ),
                        metric_value=(
                            numeric_value
                        ),
                        end_time=(
                            end_time
                        )
                    )

                    db.session.add(
                        row
                    )

                    saved_count += 1

        db.session.commit()

        return {
            "saved": saved_count
        }

    # =========================================================
    # SYNC INSIGHTS
    # =========================================================

    @classmethod
    def sync_insights(
        cls,
        mavis_user_id,
        page_id=None,
        metric=None,
        period=None,
        since=None,
        until=None
    ):

        result = cls.fetch_insights(
            mavis_user_id=mavis_user_id,
            page_id=page_id,
            metric=metric,
            period=period,
            since=since,
            until=until
        )

        save_result = (
            cls.save_insights(
                mavis_user_id=mavis_user_id,
                page_id=(
                    result["page"]["id"]
                ),
                insights=(
                    result["data"]
                )
            )
        )

        return {
            "page": result["page"],
            "insights": result["data"],
            "saved": save_result
        }

    # =========================================================
    # GET STORED INSIGHTS
    # =========================================================

    @classmethod
    def get_stored_insights(
        cls,
        mavis_user_id,
        page_id=None,
        metric_name=None,
        period=None
    ):

        query = (
            Facebook_Insights.query
            .filter_by(
                mavis_user_id=int(
                    mavis_user_id
                )
            )
        )

        if page_id:

            query = query.filter_by(
                page_id=str(
                    page_id
                )
            )

        if metric_name:

            query = query.filter_by(
                metric_name=metric_name
            )

        if period:

            query = query.filter_by(
                period=period
            )

        rows = (
            query
            .order_by(
                Facebook_Insights.end_time.desc()
            )
            .all()
        )

        return [
            {
                "id": row.id,
                "connection_id": (
                    row.connection_id
                ),
                "mavis_user_id": (
                    row.mavis_user_id
                ),
                "page_id": row.page_id,
                "page_name": row.page_name,
                "metric_name": (
                    row.metric_name
                ),
                "metric_title": (
                    row.metric_title
                ),
                "metric_description": (
                    row.metric_description
                ),
                "period": row.period,
                "metric_value": (
                    cls._safe_float(
                        row.metric_value
                    )
                ),
                "end_time": (
                    row.end_time.isoformat()
                    if row.end_time
                    else None
                ),
                "recorded_at": (
                    row.recorded_at.isoformat()
                    if row.recorded_at
                    else None
                )
            }
            for row in rows
        ]

    # =========================================================
    # FACEBOOK CONTENT
    # =========================================================
    #
    # PENTING:
    # Tidak menggunakan /feed.
    #
    # Endpoint yang dipakai:
    # /{page_id}/posts
    #
    # Hasil pengujian:
    # /feed  -> HTTP 400
    # /posts -> HTTP 200
    #
    # =========================================================

    @classmethod
    def fetch_contents(
        cls,
        mavis_user_id,
        page_id=None,
        limit=None
    ):

        connection = (
            cls.get_connection(
                mavis_user_id,
                page_id
            )
        )

        if not connection:

            raise ValueError(
                "Facebook Page belum terhubung."
            )

        token = (
            cls.get_access_token(
                connection
            )
        )

        limit = (
            cls.DEFAULT_CONTENT_LIMIT
            if limit is None
            else min(
                int(limit),
                100
            )
        )

        params = {
            "fields": (
                "id,"
                "message,"
                "created_time,"
                "permalink_url,"
                "attachments{"
                "media_type,"
                "type"
                "}"
            ),
            "limit": limit
        }

        # =====================================================
        # /posts
        # =====================================================

        data = cls._request_get(
            (
                f"/{connection.page_id}"
                "/posts"
            ),
            token,
            params
        )

        contents = []

        for item in data.get(
            "data",
            []
        ):

            attachments = (
                item.get(
                    "attachments"
                )
                or {}
            )

            attachment_data = (
                attachments.get(
                    "data",
                    []
                )
                if isinstance(
                    attachments,
                    dict
                )
                else []
            )

            content_type = (
                "POST"
            )

            if attachment_data:

                first_attachment = (
                    attachment_data[0]
                )

                media_type = (
                    first_attachment.get(
                        "media_type"
                    )
                )

                attachment_type = (
                    first_attachment.get(
                        "type"
                    )
                )

                if media_type:

                    content_type = (
                        str(
                            media_type
                        ).upper()
                    )

                elif attachment_type:

                    content_type = (
                        str(
                            attachment_type
                        ).upper()
                    )

            created_time = (
                cls._parse_datetime(
                    item.get(
                        "created_time"
                    )
                )
            )

            contents.append(
                {
                    "page_id": (
                        connection.page_id
                    ),
                    "page_name": (
                        connection.page_name
                    ),
                    "post_id": (
                        item.get("id")
                    ),
                    "content_type": (
                        content_type
                    ),
                    "message": (
                        item.get(
                            "message"
                        )
                    ),
                    "created_time": (
                        created_time
                    ),
                    "permalink_url": (
                        item.get(
                            "permalink_url"
                        )
                    ),
                    "views": 0,
                    "impressions": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "engagement": 0,
                    "raw_data": (
                        json.dumps(
                            item,
                            ensure_ascii=False
                        )
                    )
                }
            )

        return {
            "page": {
                "id": connection.page_id,
                "name": connection.page_name
            },
            "data": contents,
            "paging": (
                data.get(
                    "paging"
                )
            )
        }

    # =========================================================
    # SAVE CONTENTS
    # =========================================================

    @classmethod
    def save_contents(
        cls,
        mavis_user_id,
        page_id,
        contents
    ):

        connection = (
            cls.get_connection(
                mavis_user_id,
                page_id
            )
        )

        if not connection:

            raise ValueError(
                "Facebook connection tidak ditemukan."
            )

        saved_count = 0

        updated_count = 0

        for item in contents or []:

            post_id = str(
                item.get(
                    "post_id"
                )
                or ""
            ).strip()

            if not post_id:
                continue

            existing = (
                Facebook_Contents.query
                .filter_by(
                    connection_id=(
                        connection.id
                    ),
                    post_id=post_id
                )
                .first()
            )

            created_time = (
                item.get(
                    "created_time"
                )
            )

            if isinstance(
                created_time,
                str
            ):

                created_time = (
                    cls._parse_datetime(
                        created_time
                    )
                )

            values = {
                "mavis_user_id": (
                    int(mavis_user_id)
                ),
                "page_id": (
                    connection.page_id
                ),
                "page_name": (
                    connection.page_name
                ),
                "content_type": (
                    item.get(
                        "content_type"
                    )
                ),
                "message": (
                    item.get(
                        "message"
                    )
                ),
                "created_time": (
                    created_time
                ),
                "permalink_url": (
                    item.get(
                        "permalink_url"
                    )
                ),
                "views": (
                    cls._safe_float(
                        item.get(
                            "views"
                        )
                    )
                ),
                "impressions": (
                    cls._safe_float(
                        item.get(
                            "impressions"
                        )
                    )
                ),
                "likes": (
                    cls._safe_int(
                        item.get(
                            "likes"
                        )
                    )
                ),
                "comments": (
                    cls._safe_int(
                        item.get(
                            "comments"
                        )
                    )
                ),
                "shares": (
                    cls._safe_int(
                        item.get(
                            "shares"
                        )
                    )
                ),
                "engagement": (
                    cls._safe_float(
                        item.get(
                            "engagement"
                        )
                    )
                ),
                "raw_data": (
                    item.get(
                        "raw_data"
                    )
                )
            }

            if existing:

                for key, value in values.items():

                    setattr(
                        existing,
                        key,
                        value
                    )

                updated_count += 1

            else:

                row = Facebook_Contents(
                    connection_id=(
                        connection.id
                    ),
                    mavis_user_id=(
                        int(mavis_user_id)
                    ),
                    page_id=(
                        connection.page_id
                    ),
                    page_name=(
                        connection.page_name
                    ),
                    post_id=(
                        post_id
                    ),
                    content_type=(
                        values["content_type"]
                    ),
                    message=(
                        values["message"]
                    ),
                    created_time=(
                        values["created_time"]
                    ),
                    permalink_url=(
                        values["permalink_url"]
                    ),
                    views=(
                        values["views"]
                    ),
                    impressions=(
                        values["impressions"]
                    ),
                    likes=(
                        values["likes"]
                    ),
                    comments=(
                        values["comments"]
                    ),
                    shares=(
                        values["shares"]
                    ),
                    engagement=(
                        values["engagement"]
                    ),
                    raw_data=(
                        values["raw_data"]
                    )
                )

                db.session.add(
                    row
                )

                saved_count += 1

        db.session.commit()

        return {
            "saved": saved_count,
            "updated": updated_count,
            "total": (
                saved_count
                + updated_count
            )
        }

    # =========================================================
    # SYNC CONTENTS
    # =========================================================

    @classmethod
    def sync_contents(
        cls,
        mavis_user_id,
        page_id=None,
        limit=None
    ):

        result = cls.fetch_contents(
            mavis_user_id=mavis_user_id,
            page_id=page_id,
            limit=limit
        )

        save_result = (
            cls.save_contents(
                mavis_user_id=mavis_user_id,
                page_id=(
                    result["page"]["id"]
                ),
                contents=(
                    result["data"]
                )
            )
        )

        return {
            "page": result["page"],
            "contents": result["data"],
            "saved": save_result,
            "paging": result.get(
                "paging"
            )
        }

    # =========================================================
    # GET STORED CONTENTS
    # =========================================================

    @classmethod
    def get_stored_contents(
        cls,
        mavis_user_id,
        page_id=None,
        content_type=None,
        limit=100
    ):

        query = (
            Facebook_Contents.query
            .filter_by(
                mavis_user_id=int(
                    mavis_user_id
                )
            )
        )

        if page_id:

            query = query.filter_by(
                page_id=str(
                    page_id
                )
            )

        if content_type:

            query = query.filter_by(
                content_type=(
                    content_type
                )
            )

        rows = (
            query
            .order_by(
                Facebook_Contents.created_time.desc()
            )
            .limit(
                int(limit or 100)
            )
            .all()
        )

        return [
            {
                "id": row.id,
                "connection_id": (
                    row.connection_id
                ),
                "mavis_user_id": (
                    row.mavis_user_id
                ),
                "page_id": row.page_id,
                "page_name": row.page_name,
                "post_id": row.post_id,
                "content_type": (
                    row.content_type
                ),
                "message": row.message,
                "created_time": (
                    row.created_time.isoformat()
                    if row.created_time
                    else None
                ),
                "permalink_url": (
                    row.permalink_url
                ),
                "views": (
                    cls._safe_int(
                        row.views
                    )
                ),
                "impressions": (
                    cls._safe_int(
                        row.impressions
                    )
                ),
                "likes": (
                    cls._safe_int(
                        row.likes
                    )
                ),
                "comments": (
                    cls._safe_int(
                        row.comments
                    )
                ),
                "shares": (
                    cls._safe_int(
                        row.shares
                    )
                ),
                "engagement": (
                    cls._safe_float(
                        row.engagement
                    )
                ),
                "recorded_at": (
                    row.recorded_at.isoformat()
                    if row.recorded_at
                    else None
                ),
                "updated_at": (
                    row.updated_at.isoformat()
                    if row.updated_at
                    else None
                )
            }
            for row in rows
        ]

    # =========================================================
    # FULL SYNC
    # =========================================================

    @classmethod
    def sync(
        cls,
        mavis_user_id,
        page_id=None,
        metric=None,
        period=None,
        since=None,
        until=None,
        content_limit=None
    ):

        insight_result = (
            cls.sync_insights(
                mavis_user_id=(
                    mavis_user_id
                ),
                page_id=page_id,
                metric=metric,
                period=period,
                since=since,
                until=until
            )
        )

        content_result = (
            cls.sync_contents(
                mavis_user_id=(
                    mavis_user_id
                ),
                page_id=page_id,
                limit=content_limit
            )
        )

        return {
            "page": (
                insight_result.get(
                    "page"
                )
                or content_result.get(
                    "page"
                )
            ),
            "insights": {
                "count": len(
                    insight_result.get(
                        "insights",
                        []
                    )
                ),
                "saved": (
                    insight_result
                    .get(
                        "saved",
                        {}
                    )
                )
            },
            "contents": {
                "count": len(
                    content_result.get(
                        "contents",
                        []
                    )
                ),
                "saved": (
                    content_result
                    .get(
                        "saved",
                        {}
                    )
                )
            }
        }

    # =========================================================
    # DISCONNECT
    # =========================================================

    @classmethod
    def disconnect(
        cls,
        mavis_user_id,
        page_id=None
    ):

        query = (
            Facebook_Connections.query
            .filter_by(
                mavis_user_id=int(
                    mavis_user_id
                )
            )
        )

        if page_id:

            query = query.filter_by(
                page_id=str(
                    page_id
                )
            )

        connections = (
            query.all()
        )

        if not connections:

            return {
                "disconnected": 0
            }

        for connection in connections:

            connection.connected = False

        db.session.commit()

        return {
            "disconnected": len(
                connections
            )
        }

    # =========================================================
    # TOKEN VALIDATION
    # =========================================================

    @classmethod
    def validate_connection(
        cls,
        mavis_user_id,
        page_id=None
    ):

        connection = (
            cls.get_connection(
                mavis_user_id,
                page_id
            )
        )

        if not connection:

            return {
                "valid": False,
                "message": (
                    "Facebook Page tidak ditemukan."
                )
            }

        token = (
            cls.get_access_token(
                connection
            )
        )

        try:

            data = cls._request_get(
                "/me",
                token,
                {
                    "fields": "id,name"
                }
            )

            return {
                "valid": True,
                "message": (
                    "Facebook connection valid."
                ),
                "data": data
            }

        except Exception as e:

            return {
                "valid": False,
                "message": str(e)
            }