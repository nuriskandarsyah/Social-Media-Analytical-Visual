from extensions import db


class AIDAStage(db.Model):
    __tablename__ = "AIDAStage"

    id_aida = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    stage_name = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    # Relasi
    content_recommendations = db.relationship(
        "ContentRecommendations",
        back_populates="aida",
        cascade="all, delete-orphan"
    )