from datetime import datetime, date, timedelta
import calendar
import json

from extensions import db

from models import (
    Reports,
    Report_Evaluations,
    Report_Approvals,
    Users,
    Posts,
    Post_Metrics,
    Clusters,
    Forecast,
    Recommendations,
    ContentRecommendations
)


class ReportService:

    # =====================================================
    # HELPER SERIALIZE
    # =====================================================

    @staticmethod
    def serialize_value(value):

        if isinstance(
            value,
            (datetime, date)
        ):
            return value.isoformat()

        if isinstance(
            value,
            dict
        ):

            return {
                key: ReportService.serialize_value(
                    item
                )
                for key, item in value.items()
            }

        if isinstance(
            value,
            list
        ):

            return [
                ReportService.serialize_value(
                    item
                )
                for item in value
            ]

        return value

    # =====================================================
    # GET ALL REPORTS
    # =====================================================

    @staticmethod
    def get_all(
        month=None,
        year=None
    ):

        query = Reports.query

        if month is not None:

            query = query.filter(
                Reports.report_month
                == int(month)
            )

        if year is not None:

            query = query.filter(
                Reports.report_year
                == int(year)
            )

        reports = (
            query
            .order_by(
                Reports.report_year.desc(),
                Reports.report_month.desc()
            )
            .all()
        )

        data = []

        for report in reports:

            data.append(
                ReportService.serialize_report(
                    report
                )
            )

        return data

    # =====================================================
    # GET REPORT BY ID
    # =====================================================

    @staticmethod
    def get_by_id(
        id_report
    ):

        return (
            Reports.query
            .filter_by(
                id_report=id_report
            )
            .first()
        )

    # =====================================================
    # SERIALIZE REPORT
    # =====================================================

    @staticmethod
    def serialize_report(
        report
    ):

        evaluations = []

        for item in report.evaluations:

            evaluations.append({
                "id_evaluation": (
                    item.id_evaluation
                ),
                "id_user": (
                    item.id_user
                ),
                "evaluation": (
                    item.evaluation
                ),
                "feedback": (
                    item.feedback
                ),
                "created_at": (
                    ReportService.serialize_value(
                        item.created_at
                    )
                )
            })

        approvals = []

        for item in report.approvals:

            approvals.append({
                "id_approval": (
                    item.id_approval
                ),
                "id_user": (
                    item.id_user
                ),
                "status": (
                    item.status
                ),
                "signature_data": (
                    item.signature_data
                ),
                "approved_at": (
                    ReportService.serialize_value(
                        item.approved_at
                    )
                )
            })

        return {
            "id_report": (
                report.id_report
            ),
            "report_month": (
                report.report_month
            ),
            "report_year": (
                report.report_year
            ),
            "created_at": (
                ReportService.serialize_value(
                    report.created_at
                )
            ),
            "evaluations": evaluations,
            "approvals": approvals
        }

    # =====================================================
    # CREATE REPORT
    # =====================================================

    @staticmethod
    def create_report(
        month,
        year
    ):

        month = int(month)
        year = int(year)

        if month < 1 or month > 12:

            raise ValueError(
                "Month tidak valid"
            )

        if year < 2000 or year > 2100:

            raise ValueError(
                "Year tidak valid"
            )

        existing = (
            Reports.query
            .filter_by(
                report_month=month,
                report_year=year
            )
            .first()
        )

        if existing:

            return existing, False

        report = Reports(
            report_month=month,
            report_year=year,
            created_at=datetime.now()
        )

        db.session.add(
            report
        )

        db.session.commit()

        return report, True

    # =====================================================
    # GET REPORT DATA
    # =====================================================

    @staticmethod
    def get_report_data(
        month,
        year
    ):

        month = int(month)
        year = int(year)

        # -------------------------------------------------
        # POSTS + METRICS
        # -------------------------------------------------

        posts_query = (
            db.session.query(
                Posts,
                Post_Metrics
            )
            .join(
                Post_Metrics,
                Posts.id_posts
                == Post_Metrics.id_posts
            )
            .filter(
                db.func.month(
                    Post_Metrics.metric_date
                ) == month,
                db.func.year(
                    Post_Metrics.metric_date
                ) == year
            )
        )

        post_data = []

        for post, metric in (
            posts_query.all()
        ):

            post_data.append({
                "id_posts": (
                    post.id_posts
                ),
                "meta_post_id": (
                    post.meta_post_id
                ),
                "caption": (
                    post.caption
                ),
                "media_type": (
                    post.media_type
                ),
                "views": (
                    metric.views or 0
                ),
                "reach": (
                    metric.reach or 0
                ),
                "impressions": (
                    metric.impressions or 0
                ),
                "likes": (
                    metric.likes or 0
                ),
                "comments": (
                    metric.comments or 0
                ),
                "shares": (
                    metric.shares or 0
                ),
                "saves": (
                    metric.saves or 0
                ),
                "accounts_engaged": (
                    metric.accounts_engaged or 0
                ),
                "engagement_rate": (
                    metric.engagement_rate or 0
                ),
                "metric_date": (
                    ReportService.serialize_value(
                        metric.metric_date
                    )
                )
            })

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        total_posts = len(
            post_data
        )

        total_views = sum(
            item["views"]
            for item in post_data
        )

        total_reach = sum(
            item["reach"]
            for item in post_data
        )

        total_impressions = sum(
            item["impressions"]
            for item in post_data
        )

        total_likes = sum(
            item["likes"]
            for item in post_data
        )

        total_comments = sum(
            item["comments"]
            for item in post_data
        )

        total_shares = sum(
            item["shares"]
            for item in post_data
        )

        total_saves = sum(
            item["saves"]
            for item in post_data
        )

        if total_posts > 0:

            average_engagement = (
                sum(
                    float(
                        item[
                            "engagement_rate"
                        ]
                        or 0
                    )
                    for item in post_data
                )
                / total_posts
            )

        else:

            average_engagement = 0

        # -------------------------------------------------
        # CLUSTERS
        # -------------------------------------------------

        post_ids = [
            item["id_posts"]
            for item in post_data
        ]

        cluster_data = []

        if post_ids:

            clusters = (
                Clusters.query
                .filter(
                    Clusters.id_posts
                    .in_(post_ids)
                )
                .order_by(
                    Clusters.id_clusters.asc()
                )
                .all()
            )

            for item in clusters:

                cluster_data.append({
                    "id_clusters": (
                        item.id_clusters
                    ),
                    "id_posts": (
                        item.id_posts
                    ),
                    "cluster_label": (
                        item.cluster_label
                    ),
                    "performance_score": (
                        item.performance_score
                    ),
                    "created_at": (
                        ReportService.serialize_value(
                            item.created_at
                        )
                    )
                })

        # -------------------------------------------------
        # FORECAST
        # -------------------------------------------------

        start_date = date(
            year,
            month,
            1
        )

        last_day = calendar.monthrange(
            year,
            month
        )[1]

        end_date = date(
            year,
            month,
            last_day
        )

        forecasts = (
            Forecast.query
            .filter(
                Forecast.forecast_date
                >= start_date,
                Forecast.forecast_date
                <= end_date
            )
            .order_by(
                Forecast.forecast_date.asc()
            )
            .all()
        )

        forecast_data = []

        for item in forecasts:

            forecast_data.append({
                "id_forecast": (
                    item.id_forecast
                ),
                "id_posts": (
                    item.id_posts
                ),
                "forecast_date": (
                    ReportService.serialize_value(
                        item.forecast_date
                    )
                ),
                "predicted_engagement": (
                    float(
                        item.predicted_engagement
                        or 0
                    )
                ),
                "created_at": (
                    ReportService.serialize_value(
                        item.created_at
                    )
                )
            })

        # -------------------------------------------------
        # RECOMMENDATIONS
        # -------------------------------------------------

        recommendations = (
            Recommendations.query
            .order_by(
                Recommendations
                .generated_at.desc()
            )
            .all()
        )

        recommendation_data = []

        for item in recommendations:

            response_data = item.response

            if isinstance(
                response_data,
                str
            ):

                try:

                    response_data = json.loads(
                        response_data
                    )

                except Exception:

                    pass

            recommendation_data.append({
                "id_rec": (
                    item.id_rec
                ),
                "prompt": (
                    item.prompt
                ),
                "response": (
                    ReportService.serialize_value(
                        response_data
                    )
                ),
                "validation_score": (
                    item.validation_score
                ),
                "validation_status": (
                    item.validation_status
                ),
                "generated_at": (
                    ReportService.serialize_value(
                        item.generated_at
                    )
                )
            })

        # -------------------------------------------------
        # CONTENT RECOMMENDATIONS
        # -------------------------------------------------

        content_recommendations = (
            ContentRecommendations.query
            .filter(
                ContentRecommendations.posting_date
                >= start_date,
                ContentRecommendations.posting_date
                <= end_date
            )
            .order_by(
                ContentRecommendations
                .posting_date.asc()
            )
            .all()
        )

        content_data = []

        for item in content_recommendations:

            content_data.append({
                "id_cr": (
                    item.id_cr
                ),
                "id_rec": (
                    item.id_rec
                ),
                "id_aida": (
                    item.id_aida
                ),
                "id_pillar": (
                    item.id_pillar
                ),
                "content_title": (
                    item.content_title
                ),
                "posting_date": (
                    ReportService.serialize_value(
                        item.posting_date
                    )
                ),
                "predicted_engagement": (
                    float(
                        item.predicted_engagement
                        or 0
                    )
                ),
                "created_at": (
                    ReportService.serialize_value(
                        item.created_at
                    )
                ),
                "aida_stage": (
                    item.aida.stage_name
                    if item.aida
                    else None
                ),
                "content_pillar": (
                    item.pillar.pillar_name
                    if item.pillar
                    else None
                )
            })

        # -------------------------------------------------
        # RETURN
        # -------------------------------------------------

        return {
            "period": {
                "month": month,
                "year": year
            },

            "summary": {
                "total_posts": (
                    total_posts
                ),
                "total_views": (
                    total_views
                ),
                "total_reach": (
                    total_reach
                ),
                "total_impressions": (
                    total_impressions
                ),
                "total_likes": (
                    total_likes
                ),
                "total_comments": (
                    total_comments
                ),
                "total_shares": (
                    total_shares
                ),
                "total_saves": (
                    total_saves
                ),
                "average_engagement_rate": (
                    round(
                        average_engagement,
                        4
                    )
                )
            },

            "posts": post_data,

            "clusters": cluster_data,

            "forecasts": forecast_data,

            "recommendations": (
                recommendation_data
            ),

            "content_recommendations": (
                content_data
            )
        }

    # =====================================================
    # SAVE EVALUATION
    # MANAGER ONLY
    # =====================================================

    @staticmethod
    def save_evaluation(
        id_report,
        id_user,
        evaluation,
        feedback
    ):

        report = (
            ReportService.get_by_id(
                id_report
            )
        )

        if not report:

            raise ValueError(
                "Laporan tidak ditemukan"
            )

        user = (
            Users.query
            .filter_by(
                id=id_user
            )
            .first()
        )

        if not user:

            raise ValueError(
                "User tidak ditemukan"
            )

        if user.role != "manager":

            raise ValueError(
                "Hanya Manager yang dapat membuat evaluasi"
            )

        if not evaluation:

            raise ValueError(
                "Evaluation wajib diisi"
            )

        if not str(
            evaluation
        ).strip():

            raise ValueError(
                "Evaluation tidak boleh kosong"
            )

        item = Report_Evaluations(
            id_report=id_report,
            id_user=id_user,
            evaluation=str(
                evaluation
            ).strip(),
            feedback=(
                str(
                    feedback
                ).strip()
                if feedback
                else None
            ),
            created_at=datetime.now()
        )

        try:

            db.session.add(
                item
            )

            db.session.commit()

            return item

        except Exception:

            db.session.rollback()
            raise

    # =====================================================
    # SAVE APPROVAL
    # MANAGER ONLY
    # =====================================================

    @staticmethod
    def save_approval(
        id_report,
        id_user,
        status,
        signature_data
    ):

        report = (
            ReportService.get_by_id(
                id_report
            )
        )

        if not report:

            raise ValueError(
                "Laporan tidak ditemukan"
            )

        user = (
            Users.query
            .filter_by(
                id=id_user
            )
            .first()
        )

        if not user:

            raise ValueError(
                "User tidak ditemukan"
            )

        if user.role != "manager":

            raise ValueError(
                "Hanya Manager yang dapat melakukan approval"
            )

        allowed_status = [
            "pending",
            "approved",
            "rejected"
        ]

        if status not in allowed_status:

            raise ValueError(
                "Status approval tidak valid"
            )

        if status == "approved":

            if not signature_data:

                raise ValueError(
                    "Signature data wajib diisi "
                    "untuk approval"
                )

        approval = Report_Approvals(
            id_report=id_report,
            id_user=id_user,
            status=status,
            signature_data=(
                signature_data
            ),
            approved_at=(
                datetime.now()
                if status == "approved"
                else None
            )
        )

        try:

            db.session.add(
                approval
            )

            db.session.commit()

            return approval

        except Exception:

            db.session.rollback()
            raise

    # =====================================================
    # SERIALIZE EVALUATION
    # =====================================================

    @staticmethod
    def serialize_evaluation(
        item
    ):

        return {
            "id_evaluation": (
                item.id_evaluation
            ),
            "id_report": (
                item.id_report
            ),
            "id_user": (
                item.id_user
            ),
            "evaluation": (
                item.evaluation
            ),
            "feedback": (
                item.feedback
            ),
            "created_at": (
                ReportService.serialize_value(
                    item.created_at
                )
            )
        }

    # =====================================================
    # SERIALIZE APPROVAL
    # =====================================================

    @staticmethod
    def serialize_approval(
        item
    ):

        return {
            "id_approval": (
                item.id_approval
            ),
            "id_report": (
                item.id_report
            ),
            "id_user": (
                item.id_user
            ),
            "status": (
                item.status
            ),
            "signature_data": (
                item.signature_data
            ),
            "approved_at": (
                ReportService.serialize_value(
                    item.approved_at
                )
            )
        }