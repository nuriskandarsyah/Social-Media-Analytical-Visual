from extensions import db


class Knowledge_Base(db.Model):
    __tablename__ = "Knowledge_Base"

    id_kb = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    content = db.Column(
        db.Text
    )

    source_type = db.Column(
        db.String(255)
    )

    # Pemilik / akun Instagram yang menggunakan dokumen.
    # Nilai diambil dari session Meta aktif.
    instagram_user_id = db.Column(
        db.String(64),
        index=True
    )

    created_at = db.Column(
        db.DateTime
    )

    # Relasi ke embedding
    embeddings = db.relationship(
        "Embeddings",
        back_populates="knowledge_base",
        cascade="all, delete-orphan"
    )