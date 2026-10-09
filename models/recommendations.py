from extensions import db


class Recommendations(db.Model):
    __tablename__ = "Recommendations"

    id_rec = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    prompt = db.Column(
        db.Text
    )

    response = db.Column(
        db.Text
    )

    validation_score = db.Column(
        db.Float
    )

    validation_status = db.Column(
        db.String(255)
    )

    generated_at = db.Column(
        db.DateTime
    )

    # Relasi
    content_recommendations = db.relationship(
        "ContentRecommendations",
        back_populates="recommendation",
        cascade="all, delete-orphan"
    )