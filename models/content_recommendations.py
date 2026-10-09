from extensions import db


class ContentRecommendations(db.Model):
    __tablename__ = "ContentRecommendations"

    id_cr = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    id_rec = db.Column(
        db.Integer,
        db.ForeignKey("Recommendations.id_rec"),
        nullable=False
    )

    id_aida = db.Column(
        db.Integer,
        db.ForeignKey("AIDAStage.id_aida"),
        nullable=False
    )

    id_pillar = db.Column(
        db.Integer,
        db.ForeignKey("Content_Pillar.id_pillar"),
        nullable=False
    )

    content_title = db.Column(
        db.String(255)
    )

    posting_date = db.Column(
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
    recommendation = db.relationship(
        "Recommendations",
        back_populates="content_recommendations"
    )

    aida = db.relationship(
        "AIDAStage",
        back_populates="content_recommendations"
    )

    pillar = db.relationship(
        "Content_Pillar",
        back_populates="content_recommendations"
    )