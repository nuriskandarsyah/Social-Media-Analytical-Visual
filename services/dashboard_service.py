from sqlalchemy import func

from extensions import db

from models import (
    Posts,
    Post_Metrics,
    Account_Metrics,
    Clusters,
    Forecast,
    SyncLog
)


class DashboardService:

    @staticmethod
    def get_dashboard(month=None, year=None):

        # =====================================================
        # CEK STATUS KONEKSI INSTAGRAM DARI SYNC LOG
        # =====================================================
        # Jika koneksi terakhir diputuskan, Dashboard tidak
        # menampilkan data lama. Data database tetap aman.
        latest_sync = (
            SyncLog.query
            .order_by(
                SyncLog.sync_date.desc(),
                SyncLog.id_sync.desc()
            )
            .first()
        )

        is_disconnected = (
            latest_sync is not None
            and latest_sync.status == "DISCONNECTED"
        )

        # =====================================================
        # JIKA INSTAGRAM TERPUTUS
        # =====================================================
        if is_disconnected:
            return {
                "connected": False,

                "summary": {
                    "total_posts": 0,
                    "total_views": 0,
                    "total_reach": 0,
                    "total_impressions": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "total_shares": 0,
                    "total_saves": 0,
                    "average_engagement_rate": 0
                },

                "total_posts": 0,
                "total_content": 0,

                "account_metrics": {
                    "followers": 0,
                    "accounts_reached": 0,
                    "accounts_engaged": 0,
                    "profile_views": 0,
                    "website_clicks": 0
                },

                "clusters": [],
                "forecasts": [],
                "posts": [],

                "metrics": {
                    "views": 0,
                    "reach": 0,
                    "impressions": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "saves": 0,
                    "content_interactions": 0,
                    "engagement_rate": 0,
                    "followers": 0,
                    "accounts_reached": 0,
                    "accounts_engaged": 0,
                    "profile_views": 0,
                    "website_clicks": 0
                },

                "filter": {
                    "month": month,
                    "year": year
                }
            }


        # =====================================================
        # TOTAL POSTS
        # =====================================================

        posts_query = Posts.query

        if year:
            posts_query = posts_query.filter(
                func.year(Posts.posted_at) == year
            )

        if month:
            posts_query = posts_query.filter(
                func.month(Posts.posted_at) == month
            )

        total_posts = posts_query.count()


        # =====================================================
        # POST METRICS
        # =====================================================
        # Metric konten mengikuti tanggal upload pada Posts.posted_at,
        # bukan tanggal sinkronisasi pada Post_Metrics.metric_date.

        metrics_query = (
            db.session.query(Post_Metrics)
            .join(
                Posts,
                Posts.id_posts == Post_Metrics.id_posts
            )
        )

        if year:
            metrics_query = metrics_query.filter(
                func.year(Posts.posted_at) == year
            )

        if month:
            metrics_query = metrics_query.filter(
                func.month(Posts.posted_at) == month
            )

        metrics_summary = (
            metrics_query
            .with_entities(
                func.coalesce(
                    func.sum(Post_Metrics.views),
                    0
                ).label("total_views"),
                func.coalesce(
                    func.sum(Post_Metrics.reach),
                    0
                ).label("total_reach"),
                func.coalesce(
                    func.sum(Post_Metrics.impressions),
                    0
                ).label("total_impressions"),
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
                    func.avg(Post_Metrics.engagement_rate),
                    0
                ).label(
                    "average_engagement_rate"
                ),
                func.coalesce(
                    func.sum(Post_Metrics.content_interactions),
                    0
                ).label(
                    "total_content_interactions"
                )
            )
            .first()
        )

        # =====================================================
        # AMBIL HASIL METRICS
        # =====================================================

        if metrics_summary:

            total_views = (
                metrics_summary.total_views
                or 0
            )

            total_reach = (
                metrics_summary.total_reach
                or 0
            )

            total_impressions = (
                metrics_summary.total_impressions
                or 0
            )

            total_likes = (
                metrics_summary.total_likes
                or 0
            )

            total_comments = (
                metrics_summary.total_comments
                or 0
            )

            total_shares = (
                metrics_summary.total_shares
                or 0
            )

            total_saves = (
                metrics_summary.total_saves
                or 0
            )

            average_engagement_rate = (
                metrics_summary.average_engagement_rate
                or 0
            )

            total_content_interactions = (
                metrics_summary.total_content_interactions
                or 0
            )

        else:

            total_views = 0
            total_reach = 0
            total_impressions = 0
            total_likes = 0
            total_comments = 0
            total_shares = 0
            total_saves = 0
            average_engagement_rate = 0
            total_content_interactions = 0


        # =====================================================
        # ACCOUNT METRICS
        # =====================================================
        # Account_Metrics menyimpan snapshot account saat sync.
        # Untuk filter periode, gunakan snapshot TERAKHIR pada
        # periode tersebut. Jangan menjumlahkan snapshot karena
        # profile_views/website_clicks/reach/engaged dapat berupa
        # nilai kumulatif/snapshot.
        # =====================================================

        account_query = (
            Account_Metrics.query
            .order_by(
                Account_Metrics.metric_date.desc(),
                Account_Metrics.id_am.desc()
            )
        )

        if year:
            account_query = account_query.filter(
                func.year(
                    Account_Metrics.metric_date
                ) == year
            )

        if month:
            account_query = account_query.filter(
                func.month(
                    Account_Metrics.metric_date
                ) == month
            )

        account_metric = (
            account_query
            .first()
        )

        account_data = {
            "followers": 0,
            "accounts_reached": 0,
            "accounts_engaged": 0,
            "profile_views": 0,
            "website_clicks": 0
        }

        if account_metric:

            account_data = {
                "followers": int(
                    account_metric.followers or 0
                ),
                "accounts_reached": int(
                    account_metric.accounts_reached or 0
                ),
                "accounts_engaged": int(
                    account_metric.accounts_engaged or 0
                ),
                "profile_views": int(
                    account_metric.profile_views or 0
                ),
                "website_clicks": int(
                    account_metric.website_clicks or 0
                )
            }

        # =====================================================
        # CLUSTER SUMMARY
        # =====================================================

        cluster_query = (
            Clusters.query
            .with_entities(

                Clusters.cluster_label,

                func.count(
                    Clusters.id_clusters
                ).label(
                    "total_posts"
                ),

                func.avg(
                    Clusters.performance_score
                ).label(
                    "average_score"
                )

            )
            .group_by(
                Clusters.cluster_label
            )
        )


        cluster_data = (
            cluster_query
            .all()
        )


        clusters = []


        for cluster in cluster_data:

            clusters.append({

                "cluster_label":
                    cluster.cluster_label,

                "total_posts":
                    int(
                        cluster.total_posts
                        or 0
                    ),

                "average_score":
                    float(
                        cluster.average_score
                        or 0
                    )

            })


        # =====================================================
        # FORECAST
        # =====================================================

        forecast_query = (
            Forecast.query
            .order_by(
                Forecast.forecast_date.asc()
            )
        )


        if year:

            forecast_query = forecast_query.filter(
                func.year(
                    Forecast.forecast_date
                ) == year
            )


        if month:

            forecast_query = forecast_query.filter(
                func.month(
                    Forecast.forecast_date
                ) == month
            )


        forecasts = (
            forecast_query
            .limit(10)
            .all()
        )


        # Jika periode yang dipilih belum memiliki forecast,
        # gunakan forecast terbaru yang tersedia.
        if not forecasts and (year or month):
            forecasts = (
                Forecast.query
                .order_by(
                    Forecast.forecast_date.asc()
                )
                .limit(10)
                .all()
            )


        forecast_data = []


        for item in forecasts:

            forecast_data.append({

                "id_forecast":
                    item.id_forecast,

                "id_posts":
                    item.id_posts,

                "forecast_date": (

                    item.forecast_date.isoformat()

                    if item.forecast_date

                    else None

                ),

                "predicted_engagement":
                    float(
                        item.predicted_engagement
                        or 0
                    )

            })


        # =====================================================
        # RINGKASAN KONTEN
        # =====================================================
        # Ambil 10 konten terbaru beserta metrik terbarunya.
        recent_posts_query = Posts.query

        if year:
            recent_posts_query = recent_posts_query.filter(
                func.year(Posts.posted_at) == year
            )

        if month:
            recent_posts_query = recent_posts_query.filter(
                func.month(Posts.posted_at) == month
            )

        recent_posts = (
            recent_posts_query
            .order_by(
                Posts.posted_at.desc(),
                Posts.created_at.desc(),
                Posts.id_posts.desc()
            )
            .limit(10)
            .all()
        )

        post_data = []

        for post in recent_posts:

            latest_metric = (
                Post_Metrics.query
                .filter_by(
                    id_posts=post.id_posts
                )
                .order_by(
                    Post_Metrics.metric_date.desc()
                )
                .first()
            )

            post_data.append({
                "id_posts":
                    post.id_posts,

                "meta_post_id":
                    post.meta_post_id,

                "caption":
                    post.caption,

                "title":
                    post.caption,

                "media_type":
                    post.media_type,

                "media_product_type":
                    post.media_product_type,

                "collaboration":
                    post.collaboration,

                "posted_at": (
                    post.posted_at.isoformat()
                    if post.posted_at
                    else None
                ),

                "views": (
                    int(latest_metric.views or 0)
                    if latest_metric
                    else 0
                ),

                "reach": (
                    int(latest_metric.reach or 0)
                    if latest_metric
                    else 0
                ),

                "likes": (
                    int(latest_metric.likes or 0)
                    if latest_metric
                    else 0
                ),

                "comments": (
                    int(latest_metric.comments or 0)
                    if latest_metric
                    else 0
                ),

                "shares": (
                    int(latest_metric.shares or 0)
                    if latest_metric
                    else 0
                ),

                "saves": (
                    int(latest_metric.saves or 0)
                    if latest_metric
                    else 0
                ),

                "content_interactions": (
                    int(
                        latest_metric.content_interactions
                        or 0
                    )
                    if latest_metric
                    else 0
                ),

                "accounts_engaged": (
                    int(
                        latest_metric.accounts_engaged
                        or 0
                    )
                    if latest_metric
                    else 0
                ),

                "engagement_rate": (
                    float(
                        latest_metric.engagement_rate
                        or 0
                    )
                    if latest_metric
                    else 0
                )
            })


        # =====================================================
        # RESPONSE DASHBOARD
        # =====================================================

        return {

            "connected": True,

            "summary": {

                "total_posts":
                    int(total_posts),

                "total_views":
                    int(total_views),

                "total_reach":
                    int(total_reach),

                "total_impressions":
                    int(total_impressions),

                "total_likes":
                    int(total_likes),

                "total_comments":
                    int(total_comments),

                "total_shares":
                    int(total_shares),

                "total_saves":
                    int(total_saves),

                "average_engagement_rate":
                    float(
                        average_engagement_rate
                    )

            },

            "account_metrics":
                account_data,

            "clusters":
                clusters,

            "forecasts":
                forecast_data,

            # Alias untuk kompatibilitas frontend.
            "cluster_data":
                clusters,
            "forecast_data":
                forecast_data,

            "metrics": {

                "views":
                    int(total_views),

                "reach":
                    int(total_reach),

                "impressions":
                    int(total_impressions),

                "likes":
                    int(total_likes),

                "comments":
                    int(total_comments),

                "shares":
                    int(total_shares),

                "saves":
                    int(total_saves),

                "content_interactions":
                    int(total_content_interactions),

                "engagement_rate":
                    float(
                        average_engagement_rate
                    ),

                "followers":
                    int(
                        account_data.get(
                            "followers",
                            0
                        )
                    ),

                "accounts_reached":
                    int(
                        account_data.get(
                            "accounts_reached",
                            0
                        )
                    ),

                "accounts_engaged":
                    int(
                        account_data.get(
                            "accounts_engaged",
                            0
                        )
                    ),

                "profile_views":
                    int(
                        account_data.get(
                            "profile_views",
                            0
                        )
                    ),

                "website_clicks":
                    int(
                        account_data.get(
                            "website_clicks",
                            0
                        )
                    )

            },

            # Dipertahankan agar kompatibel dengan Dashboard.jsx.
            "total_posts":
                int(total_posts),

            "total_content":
                int(total_posts),
            "profile_views":
                int(
                    account_data.get(
                        "profile_views",
                        0
                    )
                ),

            "posts":
                post_data,

            "filter": {

                "month":
                    month,

                "year":
                    year

            }

        }
