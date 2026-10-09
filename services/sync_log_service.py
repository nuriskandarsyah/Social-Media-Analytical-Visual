from extensions import db
from models import SyncLog


class SyncLogService:

    @staticmethod
    def get_all(page=1, per_page=10):
        pagination = (
            SyncLog.query
            .order_by(
                SyncLog.sync_date.desc()
            )
            .paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        )

        data = []

        for item in pagination.items:
            data.append({
                "id_sync": item.id_sync,
                "sync_date": item.sync_date,
                "total_posts": item.total_posts or 0,
                "status": item.status,
                "message": item.message
            })

        return {
            "items": data,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages
            }
        }

    @staticmethod
    def get_by_id(id_sync):
        item = (
            SyncLog.query
            .filter_by(
                id_sync=id_sync
            )
            .first()
        )

        if not item:
            return None

        return {
            "id_sync": item.id_sync,
            "sync_date": item.sync_date,
            "total_posts": item.total_posts or 0,
            "status": item.status,
            "message": item.message
        }