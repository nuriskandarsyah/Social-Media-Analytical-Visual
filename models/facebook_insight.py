from extensions import db


class Facebook_Insights(db.Model):
    __tablename__ = "facebook_insights"

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

    metric_name = db.Column(
        db.String(100),
        nullable=False
    )

    metric_title = db.Column(
        db.String(255)
    )

    metric_description = db.Column(
        db.Text
    )

    period = db.Column(
        db.String(50),
        nullable=False
    )

    metric_value = db.Column(
        db.Numeric(20, 4),
        nullable=False,
        default=0
    )

    end_time = db.Column(
        db.DateTime
    )

    recorded_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    # Relasi
    connection = db.relationship(
        "Facebook_Connections",
        back_populates="insights"
    )