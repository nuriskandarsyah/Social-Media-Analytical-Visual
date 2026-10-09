from extensions import db


class Posts(db.Model):
    __tablename__ = "Posts"

    id_posts = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    meta_post_id = db.Column(
        db.String(255),
        nullable=False
    )

    caption = db.Column(
        db.Text
    )

    media_type = db.Column(
        db.String(255)
    )

    media_product_type = db.Column(
        db.String(255)
    )

    collaboration = db.Column(
        db.String(255)
    )

    posted_at = db.Column(
        db.DateTime
    )

    created_at = db.Column(
        db.DateTime
    )

    # Relasi
    post_metrics = db.relationship(
        "Post_Metrics",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    cluster = db.relationship(
        "Clusters",
        back_populates="post",
        uselist=False,
        cascade="all, delete-orphan"
    )

    forecasts = db.relationship(
        "Forecast",
        back_populates="post",
        cascade="all, delete-orphan"
    )