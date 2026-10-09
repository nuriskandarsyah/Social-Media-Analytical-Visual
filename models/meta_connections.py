from extensions import db


class Meta_Connections(db.Model):
    __tablename__ = "meta_connections"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        nullable=False
    )

    instagram_user_id = db.Column(
        db.String(100),
        nullable=False
    )

    username = db.Column(
        db.String(255),
        nullable=True
    )

    account_type = db.Column(
        db.String(50),
        nullable=True
    )

    profile_picture_url = db.Column(
        db.Text,
        nullable=True
    )

    access_token = db.Column(
        db.Text,
        nullable=False
    )

    token_type = db.Column(
        db.String(50),
        nullable=True,
        default="Bearer"
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=True
    )

    connected = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
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