from extensions import db


class Post_Metrics(db.Model):
    __tablename__ = "Post_Metrics"

    id_pm = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    id_posts = db.Column(
        db.Integer,
        db.ForeignKey("Posts.id_posts"),
        nullable=False
    )

    views = db.Column(
        db.Integer,
        default=0
    )

    reach = db.Column(
        db.Integer,
        default=0
    )

    impressions = db.Column(
        db.Integer,
        default=0
    )

    likes = db.Column(
        db.Integer,
        default=0
    )

    comments = db.Column(
        db.Integer,
        default=0
    )

    shares = db.Column(
        db.Integer,
        default=0
    )

    saves = db.Column(
        db.Integer,
        default=0
    )

    accounts_engaged = db.Column(
        db.Integer,
        default=0
    )

    content_interactions = db.Column(
        db.Integer,
        default=0
    )

    engagement_rate = db.Column(
        db.Float,
        default=0
    )

    metric_date = db.Column(
        db.DateTime
    )

    # Relasi
    post = db.relationship(
        "Posts",
        back_populates="post_metrics"
    )