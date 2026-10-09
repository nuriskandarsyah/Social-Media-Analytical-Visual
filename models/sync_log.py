from extensions import db


class SyncLog(db.Model):
    __tablename__ = "SyncLog"

    id_sync = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    sync_date = db.Column(
        db.DateTime
    )

    total_posts = db.Column(
        db.Integer,
        default=0
    )

    status = db.Column(
        db.String(255)
    )

    message = db.Column(
        db.Text
    )