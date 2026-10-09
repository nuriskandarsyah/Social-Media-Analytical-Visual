from extensions import db


class Embeddings(db.Model):
    __tablename__ = "Embeddings"

    id_embeddings = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    id_kb = db.Column(
        db.Integer,
        db.ForeignKey("Knowledge_Base.id_kb"),
        nullable=False
    )

    vector_data = db.Column(
        db.Text
    )

    model_name = db.Column(
        db.String(255)
    )

    created_at = db.Column(
        db.DateTime
    )

    # Relasi
    knowledge_base = db.relationship(
        "Knowledge_Base",
        back_populates="embeddings"
    )