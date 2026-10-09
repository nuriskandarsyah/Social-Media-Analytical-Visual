from sqlalchemy import func, desc, asc

from extensions import db

from models import (
    Posts,
    Post_Metrics,
    Account_Metrics
)


class MetaInsightService:

    # =========================================================
    # QUERY HELPER
    # =========================================================
    @staticmethod
    def _base_query():
        """
        Query utama Meta Insight.

        Setiap post dihubungkan dengan Post_Metrics melalui id_posts.
        """
        return (
            db.session.query(
                Posts,
                Post_Metrics
            )
            .join(
                Post_Metrics,
                Posts.id_posts == Post_Metrics.id_posts
            )
        )

    @staticmethod
    def _apply_filter(query, month=None, year=None):
        """
        Filter berdasarkan tanggal posting konten, bukan tanggal sync metric.

        Ini penting karena Post_Metrics.metric_date adalah tanggal
        pengambilan/sinkronisasi metric, sedangkan analisis performa
        konten seharusnya mengikuti tanggal post.
        """
        if month:
            query = query.filter(
                db.func.month(Posts.posted_at) == int(month)
            )

        if year:
            query = query.filter(
                db.func.year(Posts.posted_at) == int(year)
            )

        return query

    @staticmethod
    def _safe_float(value):
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _safe_int(value):
        try:
            return int(float(value or 0))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _engagement(metric):
        return (
            MetaInsightService._safe_int(metric.likes)
            + MetaInsightService._safe_int(metric.comments)
            + MetaInsightService._safe_int(metric.shares)
            + MetaInsightService._safe_int(metric.saves)
        )

    # =========================================================
    # GET ALL POST PERFORMANCE
    # =========================================================
    @staticmethod
    def get_post_performance(month=None, year=None):
        query = MetaInsightService._base_query()
        query = MetaInsightService._apply_filter(
            query,
            month,
            year
        )

        query = query.order_by(
            Posts.posted_at.desc()
        )

        results = query.all()

        data = []

        for post, metric in results:
            total_engagement = (
                MetaInsightService._engagement(metric)
            )

            data.append({
                "id_posts": post.id_posts,
                "meta_post_id": post.meta_post_id,
                "caption": post.caption,
                "media_type": post.media_type,
                "media_product_type": post.media_product_type,
                "collaboration": post.collaboration,
                "posted_at": (
                    post.posted_at.isoformat()
                    if post.posted_at
                    else None
                ),
                "views": MetaInsightService._safe_int(
                    metric.views
                ),
                "reach": MetaInsightService._safe_int(
                    metric.reach
                ),
                "impressions": MetaInsightService._safe_int(
                    metric.impressions
                ),
                "likes": MetaInsightService._safe_int(
                    metric.likes
                ),
                "comments": MetaInsightService._safe_int(
                    metric.comments
                ),
                "shares": MetaInsightService._safe_int(
                    metric.shares
                ),
                "saves": MetaInsightService._safe_int(
                    metric.saves
                ),
                "accounts_engaged": MetaInsightService._safe_int(
                    metric.accounts_engaged
                ),
                "content_interactions": MetaInsightService._safe_int(
                    metric.content_interactions
                    if metric.content_interactions is not None
                    else (
                        (metric.likes or 0)
                        + (metric.comments or 0)
                        + (metric.shares or 0)
                        + (metric.saves or 0)
                    )
                ),
                "total_engagement": total_engagement,
                "engagement_rate": MetaInsightService._safe_float(
                    metric.engagement_rate
                ),
                "metric_date": (
                    metric.metric_date.isoformat()
                    if metric.metric_date
                    else None
                ),
            })

        return data

    # =========================================================
    # GET SUMMARY
    # =========================================================
    @staticmethod
    def get_summary(month=None, year=None):
        query = MetaInsightService._base_query()
        query = MetaInsightService._apply_filter(
            query,
            month,
            year
        )

        rows = query.all()

        if not rows:
            return {
                "total_data": 0,
                "total_posts": 0,
                "total_views": 0,
                "total_reach": 0,
                "total_impressions": 0,
                "total_likes": 0,
                "total_comments": 0,
                "total_shares": 0,
                "total_saves": 0,
                "total_engagement": 0,
                "total_content_interactions": 0,
                "average_engagement_rate": 0.0,
            }

        total_views = 0
        total_reach = 0
        total_impressions = 0
        total_likes = 0
        total_comments = 0
        total_shares = 0
        total_saves = 0
        total_engagement = 0
        total_interactions = 0
        engagement_rates = []

        for _, metric in rows:
            total_views += MetaInsightService._safe_int(
                metric.views
            )
            total_reach += MetaInsightService._safe_int(
                metric.reach
            )
            total_impressions += MetaInsightService._safe_int(
                metric.impressions
            )
            total_likes += MetaInsightService._safe_int(
                metric.likes
            )
            total_comments += MetaInsightService._safe_int(
                metric.comments
            )
            total_shares += MetaInsightService._safe_int(
                metric.shares
            )
            total_saves += MetaInsightService._safe_int(
                metric.saves
            )
            total_engagement += (
                MetaInsightService._engagement(metric)
            )
            total_interactions += MetaInsightService._safe_int(
                metric.content_interactions
                if metric.content_interactions is not None
                else (
                    (metric.likes or 0)
                    + (metric.comments or 0)
                    + (metric.shares or 0)
                    + (metric.saves or 0)
                )
            )
            engagement_rates.append(
                MetaInsightService._safe_float(
                    metric.engagement_rate
                )
            )

        return {
            "total_data": len(rows),
            "total_posts": len(rows),
            "total_views": total_views,
            "total_reach": total_reach,
            "total_impressions": total_impressions,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_saves": total_saves,
            "total_engagement": total_engagement,
            "total_content_interactions": total_interactions,
            "average_engagement_rate": (
                sum(engagement_rates) / len(engagement_rates)
                if engagement_rates
                else 0.0
            ),
        }

    # =========================================================
    # GET ACCOUNT METRIC TERBARU
    # =========================================================
    @staticmethod
    def get_latest_account_metrics():
        """
        Ambil account metric terakhir yang tersedia.

        Tidak membuat data baru dan tidak memakai dummy.
        """
        metric = (
            Account_Metrics.query
            .order_by(
                Account_Metrics.metric_date.desc()
            )
            .first()
        )

        if not metric:
            return {
                "followers": 0,
                "accounts_reached": 0,
                "accounts_engaged": 0,
                "profile_views": 0,
                "website_clicks": 0,
                "metric_date": None,
            }

        return {
            "followers": MetaInsightService._safe_int(
                metric.followers
            ),
            "accounts_reached": MetaInsightService._safe_int(
                metric.accounts_reached
            ),
            "accounts_engaged": MetaInsightService._safe_int(
                metric.accounts_engaged
            ),
            "profile_views": MetaInsightService._safe_int(
                metric.profile_views
            ),
            "website_clicks": MetaInsightService._safe_int(
                metric.website_clicks
            ),
            "metric_date": (
                metric.metric_date.isoformat()
                if metric.metric_date
                else None
            ),
        }

    # =========================================================
    # BEST PERFORMING CONTENT
    # =========================================================
    @staticmethod
    def get_best_content(limit=5, month=None, year=None):
        query = MetaInsightService._base_query()
        query = MetaInsightService._apply_filter(
            query,
            month,
            year
        )

        query = query.order_by(
            desc(Post_Metrics.engagement_rate),
            desc(Post_Metrics.likes + Post_Metrics.comments)
        ).limit(int(limit or 5))

        results = query.all()

        return [
            MetaInsightService._format_content(
                post,
                metric
            )
            for post, metric in results
        ]

    # =========================================================
    # WORST PERFORMING CONTENT
    # =========================================================
    @staticmethod
    def get_worst_content(limit=5, month=None, year=None):
        query = MetaInsightService._base_query()
        query = MetaInsightService._apply_filter(
            query,
            month,
            year
        )

        query = query.order_by(
            asc(Post_Metrics.engagement_rate),
            asc(Post_Metrics.likes + Post_Metrics.comments)
        ).limit(int(limit or 5))

        results = query.all()

        return [
            MetaInsightService._format_content(
                post,
                metric
            )
            for post, metric in results
        ]

    # =========================================================
    # BEST BY REACH
    # =========================================================
    @staticmethod
    def get_best_by_reach(limit=5, month=None, year=None):
        query = MetaInsightService._base_query()
        query = MetaInsightService._apply_filter(
            query,
            month,
            year
        )

        results = (
            query
            .order_by(
                desc(Post_Metrics.reach)
            )
            .limit(int(limit or 5))
            .all()
        )

        return [
            MetaInsightService._format_content(
                post,
                metric
            )
            for post, metric in results
        ]

    # =========================================================
    # BEST BY ENGAGEMENT
    # =========================================================
    @staticmethod
    def get_best_by_engagement(limit=5, month=None, year=None):
        engagement = (
            func.coalesce(Post_Metrics.likes, 0)
            + func.coalesce(Post_Metrics.comments, 0)
            + func.coalesce(Post_Metrics.shares, 0)
            + func.coalesce(Post_Metrics.saves, 0)
        )

        query = MetaInsightService._base_query()
        query = MetaInsightService._apply_filter(
            query,
            month,
            year
        )

        results = (
            query
            .order_by(desc(engagement))
            .limit(int(limit or 5))
            .all()
        )

        data = []

        for post, metric in results:
            item = MetaInsightService._format_content(
                post,
                metric
            )
            item["total_engagement"] = (
                MetaInsightService._engagement(metric)
            )
            data.append(item)

        return data

    # =========================================================
    # PERFORMANCE BY MEDIA TYPE
    # =========================================================
    @staticmethod
    def get_media_performance(month=None, year=None):
        query = (
            db.session.query(
                Posts.media_type,
                func.count(
                    Posts.id_posts
                ).label("total_posts"),
                func.coalesce(
                    func.sum(Post_Metrics.views),
                    0
                ).label("total_views"),
                func.coalesce(
                    func.sum(Post_Metrics.reach),
                    0
                ).label("total_reach"),
                func.coalesce(
                    func.sum(Post_Metrics.likes),
                    0
                ).label("total_likes"),
                func.coalesce(
                    func.sum(Post_Metrics.comments),
                    0
                ).label("total_comments"),
                func.coalesce(
                    func.sum(Post_Metrics.shares),
                    0
                ).label("total_shares"),
                func.coalesce(
                    func.sum(Post_Metrics.saves),
                    0
                ).label("total_saves"),
                func.coalesce(
                    func.avg(
                        Post_Metrics.engagement_rate
                    ),
                    0
                ).label("average_engagement_rate")
            )
            .join(
                Post_Metrics,
                Posts.id_posts == Post_Metrics.id_posts
            )
        )

        query = MetaInsightService._apply_filter(
            query,
            month,
            year
        )

        query = (
            query
            .group_by(Posts.media_type)
            .order_by(
                desc(
                    func.avg(
                        Post_Metrics.engagement_rate
                    )
                )
            )
        )

        results = query.all()

        return [
            {
                "media_type": media_type,
                "total_posts": MetaInsightService._safe_int(
                    total_posts
                ),
                "total_views": MetaInsightService._safe_int(
                    total_views
                ),
                "total_reach": MetaInsightService._safe_int(
                    total_reach
                ),
                "total_likes": MetaInsightService._safe_int(
                    total_likes
                ),
                "total_comments": MetaInsightService._safe_int(
                    total_comments
                ),
                "total_shares": MetaInsightService._safe_int(
                    total_shares
                ),
                "total_saves": MetaInsightService._safe_int(
                    total_saves
                ),
                "average_engagement_rate":
                    MetaInsightService._safe_float(
                        average_engagement_rate
                    ),
            }
            for (
                media_type,
                total_posts,
                total_views,
                total_reach,
                total_likes,
                total_comments,
                total_shares,
                total_saves,
                average_engagement_rate
            ) in results
        ]

    # =========================================================
    # GENERATE INSIGHT
    # =========================================================
    @staticmethod
    def generate_insight(month=None, year=None):
        summary = MetaInsightService.get_summary(
            month=month,
            year=year
        )

        account_metrics = (
            MetaInsightService
            .get_latest_account_metrics()
        )

        best_content = (
            MetaInsightService
            .get_best_content(
                limit=1,
                month=month,
                year=year
            )
        )

        worst_content = (
            MetaInsightService
            .get_worst_content(
                limit=1,
                month=month,
                year=year
            )
        )

        best_by_engagement = (
            MetaInsightService
            .get_best_by_engagement(
                limit=1,
                month=month,
                year=year
            )
        )

        media_performance = (
            MetaInsightService
            .get_media_performance(
                month=month,
                year=year
            )
        )

        insights = []

        if summary["total_posts"] == 0:
            insights.append(
                "Belum terdapat data performa konten."
            )

            return {
                "summary": summary,
                "account_metrics": account_metrics,
                "insights": insights,
                "best_content": [],
                "worst_content": [],
                "best_by_engagement": [],
                "media_performance": []
            }

        if best_content:
            best = best_content[0]

            insights.append(
                "Konten dengan engagement rate tertinggi "
                f"adalah {best['meta_post_id']} "
                f"dengan engagement rate "
                f"{best['engagement_rate']:.2f}%."
            )

        if best_by_engagement:
            best_engagement = best_by_engagement[0]

            insights.append(
                "Konten dengan total engagement tertinggi "
                f"adalah {best_engagement['meta_post_id']} "
                f"dengan total engagement "
                f"{best_engagement['total_engagement']}."
            )

        if worst_content:
            worst = worst_content[0]

            insights.append(
                "Konten dengan engagement rate terendah "
                f"adalah {worst['meta_post_id']} "
                f"dengan engagement rate "
                f"{worst['engagement_rate']:.2f}%."
            )

        if media_performance:
            best_media = media_performance[0]
            media_name = (
                best_media["media_type"]
                or "Tidak diketahui"
            )

            insights.append(
                "Jenis media dengan rata-rata engagement "
                "rate tertinggi adalah "
                f"{media_name} dengan "
                f"{best_media['average_engagement_rate']:.2f}%."
            )

        if summary["total_engagement"] > 0:
            insights.append(
                "Total engagement dari seluruh konten adalah "
                f"{summary['total_engagement']}."
            )

        return {
            "summary": summary,
            "account_metrics": account_metrics,
            "insights": insights,
            "best_content": best_content,
            "worst_content": worst_content,
            "best_by_engagement": best_by_engagement,
            "media_performance": media_performance
        }

    # =========================================================
    # FORMAT CONTENT
    # =========================================================
    @staticmethod
    def _format_content(post, metric):
        return {
            "id_posts": post.id_posts,
            "meta_post_id": post.meta_post_id,
            "caption": post.caption,
            "media_type": post.media_type,
            "media_product_type": post.media_product_type,
            "collaboration": post.collaboration,
            "posted_at": (
                post.posted_at.isoformat()
                if post.posted_at
                else None
            ),
            "views": MetaInsightService._safe_int(
                metric.views
            ),
            "reach": MetaInsightService._safe_int(
                metric.reach
            ),
            "impressions": MetaInsightService._safe_int(
                metric.impressions
            ),
            "likes": MetaInsightService._safe_int(
                metric.likes
            ),
            "comments": MetaInsightService._safe_int(
                metric.comments
            ),
            "shares": MetaInsightService._safe_int(
                metric.shares
            ),
            "saves": MetaInsightService._safe_int(
                metric.saves
            ),
            "accounts_engaged": MetaInsightService._safe_int(
                metric.accounts_engaged
            ),
            "content_interactions": MetaInsightService._safe_int(
                metric.content_interactions
            ),
            "total_engagement": (
                MetaInsightService._engagement(metric)
            ),
            "engagement_rate": (
                MetaInsightService._safe_float(
                    metric.engagement_rate
                )
            ),
            "metric_date": (
                metric.metric_date.isoformat()
                if metric.metric_date
                else None
            ),
        }
