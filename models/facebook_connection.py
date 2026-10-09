from extensions import db


class Facebook_Connections(db.Model):
    __tablename__ = "facebook_connections"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    mavis_user_id = db.Column(
        db.BigInteger,
        nullable=False
    )

    facebook_user_id = db.Column(
        db.String(64),
        nullable=False
    )

    facebook_user_name = db.Column(
        db.String(255)
    )

    page_id = db.Column(
        db.String(64),
        nullable=False
    )

    page_name = db.Column(
        db.String(255),
        nullable=False
    )

    page_category = db.Column(
        db.String(255)
    )

    page_access_token = db.Column(
        db.Text,
        nullable=False
    )

    expires_in = db.Column(
        db.BigInteger
    )

    expires_at = db.Column(
        db.DateTime
    )

    connected = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    connected_at = db.Column(
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

    # Relasi
    insights = db.relationship(
        "Facebook_Insights",
        back_populates="connection",
        cascade="all, delete-orphan"
    )

    contents = db.relationship(
        "Facebook_Contents",
        back_populates="connection",
        cascade="all, delete-orphan"
    )