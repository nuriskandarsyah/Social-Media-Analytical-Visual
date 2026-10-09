from extensions import db


class Report_Evaluations(db.Model):
    __tablename__ = "Report_Evaluations"

    id_evaluation = db.Column(
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

    evaluation = db.Column(
        db.Text
    )

    feedback = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime
    )

    # Relasi
    report = db.relationship(
        "Reports",
        back_populates="evaluations"
    )

    user = db.relationship(
        "Users",
        back_populates="evaluations"
    )