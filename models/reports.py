from extensions import db


class Reports(db.Model):
    __tablename__ = "Reports"

    id_report = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    report_month = db.Column(
        db.Integer,
        nullable=False
    )

    report_year = db.Column(
        db.Integer,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime
    )

    # Relasi
    evaluations = db.relationship(
        "Report_Evaluations",
        back_populates="report",
        cascade="all, delete-orphan"
    )

    approvals = db.relationship(
        "Report_Approvals",
        back_populates="report",
        cascade="all, delete-orphan"
    )