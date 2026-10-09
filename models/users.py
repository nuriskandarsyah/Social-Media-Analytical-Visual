from extensions import db


class Users(db.Model):
    __tablename__ = "Users"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    username = db.Column(
        db.String(255),
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.Enum("admin", "manager"),
        nullable=False,
        default="admin"
    )

    # Relasi
    evaluations = db.relationship(
        "Report_Evaluations",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    approvals = db.relationship(
        "Report_Approvals",
        back_populates="user",
        cascade="all, delete-orphan"
    )