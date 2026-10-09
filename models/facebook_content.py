from extensions import db


class Facebook_Contents(db.Model):
    __tablename__ = "facebook_contents"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    connection_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "facebook_connections.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    mavis_user_id = db.Column(
        db.BigInteger,
        nullable=False
    )

    page_id = db.Column(
        db.String(64),
        nullable=False
    )

    page_name = db.Column(
        db.String(255)
    )

    post_id = db.Column(
        db.String(128),
        nullable=False
    )

    content_type = db.Column(
        db.String(50)
    )

    message = db.Column(
        db.Text
    )

    created_time = db.Column(
        db.DateTime
    )

    permalink_url = db.Column(
        db.Text
    )

    views = db.Column(
        db.Numeric(20, 4),
        nullable=False,
        default=0
    )

    impressions = db.Column(
        db.Numeric(20, 4),
        nullable=False,
        default=0
    )

    likes = db.Column(
        db.BigInteger,
        nullable=False,
        default=0
    )

    comments = db.Column(
        db.BigInteger,
        nullable=False,
        default=0
    )

    shares = db.Column(
        db.BigInteger,
        nullable=False,
        default=0
    )

    engagement = db.Column(
        db.Numeric(20, 4),
        nullable=False,
        default=0
    )

    recorded_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    raw_data = db.Column(
        db.Text
    )

    # Relasi
    connection = db.relationship(
        "Facebook_Connections",
        back_populates="contents"
    )