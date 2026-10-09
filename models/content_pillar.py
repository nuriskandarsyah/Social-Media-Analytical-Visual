from extensions import db


class Content_Pillar(db.Model):
    __tablename__ = "Content_Pillar"

    id_pillar = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    pillar_name = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    # Relasi
    content_recommendations = db.relationship(
        "ContentRecommendations",
        back_populates="pillar",
        cascade="all, delete-orphan"
    )