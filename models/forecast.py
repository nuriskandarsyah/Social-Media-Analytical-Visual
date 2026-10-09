from extensions import db


class Forecast(db.Model):
    __tablename__ = "Forecast"

    id_forecast = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    id_posts = db.Column(
        db.Integer,
        db.ForeignKey("Posts.id_posts"),
        nullable=False
    )

    forecast_date = db.Column(
        db.Date
    )

    predicted_engagement = db.Column(
        db.Float,
        default=0
    )

    created_at = db.Column(
        db.DateTime
    )

    # Relasi
    post = db.relationship(
        "Posts",
        back_populates="forecasts"
    )