from extensions import db


class Report_Approvals(db.Model):
    __tablename__ = "Report_Approvals"

    id_approval = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    id_report = db.Column(
        db.Integer,
        db.ForeignKey("Reports.id_report"),
        nullable=False
    )

    id_user = db.Column(
        db.Integer,
        db.ForeignKey("Users.id"),
        nullable=False
    )

    status = db.Column(
        db.Enum("pending", "approved", "rejected"),
        nullable=False,
        default="pending"
    )

    signature_data = db.Column(
        db.Text
    )

    approved_at = db.Column(
        db.DateTime
    )

    # Relasi
    report = db.relationship(
        "Reports",
        back_populates="approvals"
    )

    user = db.relationship(
        "Users",
        back_populates="approvals"
    )