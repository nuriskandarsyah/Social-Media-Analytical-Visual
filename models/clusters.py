from extensions import db


class Clusters(db.Model):
    __tablename__ = "Clusters"

    id_clusters = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    id_posts = db.Column(
        db.Integer,
        db.ForeignKey("Posts.id_posts"),
        nullable=False
    )

    cluster_label = db.Column(
        db.String(255)
    )

    performance_score = db.Column(
        db.Float,
        default=0
    )

    created_at = db.Column(
        db.DateTime
    )

    # Relasi
    post = db.relationship(
        "Posts",
        back_populates="cluster"
    )