from extensions import db


class Account_Metrics(db.Model):

    __tablename__ = "Account_Metrics"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id_am = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    # =====================================================
    # ACCOUNT METRICS
    # =====================================================

    followers = db.Column(
        db.Integer,
        default=0
    )

    accounts_reached = db.Column(
        db.Integer,
        default=0
    )

    accounts_engaged = db.Column(
        db.Integer,
        default=0
    )

    profile_views = db.Column(
        db.Integer,
        default=0
    )

    website_clicks = db.Column(
        db.Integer,
        default=0
    )

    # =====================================================
    # DATE
    # =====================================================

    metric_date = db.Column(
        db.DateTime
    )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def to_dict(self):

        return {

            "id_am":
                self.id_am,

            "followers":
                self.followers or 0,

            "accounts_reached":
                self.accounts_reached or 0,

            "accounts_engaged":
                self.accounts_engaged or 0,

            "profile_views":
                self.profile_views or 0,

            "website_clicks":
                self.website_clicks or 0,

            "metric_date":
                (
                    self.metric_date.isoformat()
                    if self.metric_date
                    else None
                )

        }
