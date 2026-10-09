from datetime import datetime, timedelta

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression

from extensions import db
from models import (
    Posts,
    Post_Metrics,
    Clusters,
    Forecast,
    Recommendations
)


class AIAnalysisService:

    @staticmethod
    def _to_datetime(value):
        """Normalisasi nilai tanggal menjadi datetime atau None."""
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.combine(value, datetime.min.time())
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_date(value):
        """Normalisasi nilai tanggal menjadi date atau None."""
        dt = AIAnalysisService._to_datetime(value)
        return dt.date() if dt else None

    @staticmethod
    def _data_date(item):
        """Ambil tanggal observasi utama dari data."""
        return (
            AIAnalysisService._to_datetime(item.get("metric_date"))
            or AIAnalysisService._to_datetime(item.get("posted_at"))
        )

    @staticmethod
    def load_data(month=None, year=None):
        query = (
            db.session.query(
                Posts,
                Post_Metrics
            )
            .join(
                Post_Metrics,
                Posts.id_posts == Post_Metrics.id_posts
            )
        )

        if month:
            query = query.filter(
                db.func.month(
                    Posts.posted_at
                ) == month
            )

        if year:
            query = query.filter(
                db.func.year(
                    Posts.posted_at
                ) == year
            )

        results = query.all()

        data = []

        for post, metric in results:
            likes = metric.likes or 0
            comments = metric.comments or 0
            shares = metric.shares or 0
            saves = metric.saves or 0
            engagement = (
                metric.content_interactions
                if metric.content_interactions is not None
                else (
                    likes
                    + comments
                    + shares
                    + saves
                )
            )

            data.append({
                "id_posts": post.id_posts,
                "meta_post_id": post.meta_post_id,
                "caption": post.caption,
                "media_type": post.media_type,
                "media_product_type": post.media_product_type,
                "posted_at": post.posted_at,
                "views": metric.views or 0,
                "likes": likes,
                "comments": comments,
                "engagement": engagement,
                "reach": metric.reach or 0,
                "impressions": metric.impressions or 0,
                "shares": shares,
                "saves": saves,
                "content_interactions": (
                    metric.content_interactions
                    if metric.content_interactions is not None
                    else engagement
                ),
                "accounts_engaged": (
                    metric.accounts_engaged or 0
                ),
                "metric_date": metric.metric_date
            })

        data.sort(
            key=lambda x: (AIAnalysisService._data_date(x) or datetime.min)
        )

        return data

    @staticmethod
    def preprocess_data(data):
        if not data:
            return {
                "features": [],
                "normalized_features": []
            }

        features = np.array([
            [
                item["views"],
                item["likes"],
                item["comments"],
                item["engagement"]
            ]
            for item in data
        ], dtype=float)

        scaler = MinMaxScaler()
        normalized = scaler.fit_transform(features)

        return {
            "features": features.tolist(),
            "normalized_features": normalized.tolist()
        }

    @staticmethod
    def clustering(data):
        total_data = len(data)

        if total_data == 0:
            return {
                "total_data": 0,
                "cluster_count": 0,
                "method": "K-Means++",
                "results": [],
                "distribution": {},
                "centroids": []
            }

        n_clusters = min(3, total_data)

        if total_data == 1:
            result = dict(data[0])
            result["cluster"] = 0
            result["cluster_label"] = "Tinggi"

            return {
                "total_data": 1,
                "cluster_count": 1,
                "method": "K-Means++",
                "results": [result],
                "distribution": {
                    "Tinggi": 1
                },
                "centroids": []
            }

        preprocessing = (
            AIAnalysisService
            .preprocess_data(data)
        )

        normalized = np.array(
            preprocessing["normalized_features"]
        )

        model = KMeans(
            n_clusters=n_clusters,
            init="k-means++",
            random_state=42,
            n_init=10
        )

        labels = model.fit_predict(
            normalized
        )

        centroids = model.cluster_centers_

        cluster_scores = {}

        for cluster_id in range(n_clusters):
            indexes = [
                i
                for i, label in enumerate(labels)
                if label == cluster_id
            ]

            if indexes:
                score = np.mean([
                    data[i]["engagement"]
                    for i in indexes
                ])

                cluster_scores[
                    cluster_id
                ] = score

        sorted_clusters = sorted(
            cluster_scores,
            key=cluster_scores.get
        )

        cluster_names = {}

        if n_clusters == 3:
            cluster_names[
                sorted_clusters[0]
            ] = "Rendah"

            cluster_names[
                sorted_clusters[1]
            ] = "Sedang"

            cluster_names[
                sorted_clusters[2]
            ] = "Tinggi"

        elif n_clusters == 2:
            cluster_names[
                sorted_clusters[0]
            ] = "Rendah"

            cluster_names[
                sorted_clusters[1]
            ] = "Tinggi"

        else:
            cluster_names[
                sorted_clusters[0]
            ] = "Tinggi"

        results = []

        for i, item in enumerate(data):
            cluster_id = int(labels[i])

            result = dict(item)
            result["cluster"] = cluster_id
            result["cluster_label"] = cluster_names[
                cluster_id
            ]

            results.append(result)

        distribution = {}

        for result in results:
            label = result["cluster_label"]

            distribution[label] = (
                distribution.get(label, 0) + 1
            )

        return {
            "total_data": total_data,
            "cluster_count": n_clusters,
            "method": "K-Means++",
            "results": results,
            "distribution": distribution,
            "centroids": centroids.tolist()
        }

    @staticmethod
    def cluster_summary(clustered_data):
        summary = {}

        for item in clustered_data:
            label = item["cluster_label"]

            if label not in summary:
                summary[label] = {
                    "cluster": label,
                    "total_posts": 0,
                    "average_views": 0,
                    "average_likes": 0,
                    "average_comments": 0,
                    "average_engagement": 0
                }

            summary[label]["total_posts"] += 1
            summary[label]["average_views"] += item["views"]
            summary[label]["average_likes"] += item["likes"]
            summary[label]["average_comments"] += item["comments"]
            summary[label]["average_engagement"] += item["engagement"]

        for value in summary.values():
            total = value["total_posts"]

            value["average_views"] /= total
            value["average_likes"] /= total
            value["average_comments"] /= total
            value["average_engagement"] /= total

        return list(summary.values())

    @staticmethod
    def generate_ai_insight(data):
        if not data:
            return {
                "best_content": None,
                "best_engagement": 0,
                "best_content_type": None,
                "insight": "Belum terdapat data.",
                "trend": "Stabil",
                "growth_percentage": 0,
                "prediction": None,
                "strategy": []
            }

        best = max(
            data,
            key=lambda x: x["engagement"]
        )

        content_groups = {}

        for item in data:
            content_type = (
                item["media_type"]
                or "UNKNOWN"
            )

            content_groups.setdefault(
                content_type,
                []
            )

            content_groups[
                content_type
            ].append(
                item["engagement"]
            )

        content_average = {
            key: sum(values) / len(values)
            for key, values in content_groups.items()
        }

        best_type = max(
            content_average,
            key=content_average.get
        )

        sorted_data = sorted(
            data,
            key=lambda x: (AIAnalysisService._data_date(x) or datetime.min)
        )

        first_engagement = (
            sorted_data[0]["engagement"]
        )

        last_engagement = (
            sorted_data[-1]["engagement"]
        )

        if last_engagement > first_engagement:
            trend = "Naik"

        elif last_engagement < first_engagement:
            trend = "Turun"

        else:
            trend = "Stabil"

        if first_engagement > 0:
            growth = (
                (
                    last_engagement
                    - first_engagement
                )
                / first_engagement
            ) * 100
        else:
            growth = 0

        if growth > 50:
            insight_level = (
                "Performa sangat dominan."
            )

        elif growth > 20:
            insight_level = (
                "Performa menunjukkan tren kuat."
            )

        else:
            insight_level = (
                "Performa relatif stabil."
            )

        insight = (
            f"Konten dengan engagement tertinggi "
            f"adalah {best['meta_post_id']} "
            f"dengan engagement {best['engagement']}. "
            f"Jenis konten dengan rata-rata engagement "
            f"tertinggi adalah {best_type}. "
            f"{insight_level}"
        )

        if trend == "Naik":
            prediction = (
                "Performa engagement menunjukkan "
                "kecenderungan meningkat."
            )

        elif trend == "Turun":
            prediction = (
                "Performa engagement menunjukkan "
                "kecenderungan menurun sehingga "
                "perlu dilakukan evaluasi konten."
            )

        else:
            prediction = (
                "Performa engagement relatif stabil."
            )

        strategy = [
            (
                f"Prioritaskan konten {best_type} "
                f"karena memiliki rata-rata "
                f"engagement tertinggi."
            ),
            (
                f"Jadikan {best['meta_post_id']} "
                f"sebagai referensi pengembangan "
                f"konten berikutnya."
            ),
            (
                "Evaluasi kembali konten dengan "
                "engagement rendah."
            )
        ]

        return {
            "best_content": best["meta_post_id"],
            "best_engagement": best["engagement"],
            "best_content_type": best_type,
            "insight": insight,
            "trend": trend,
            "growth_percentage": growth,
            "prediction": prediction,
            "strategy": strategy
        }

    @staticmethod
    def forecast_engagement(data):
        if len(data) < 2:
            return []

        sorted_data = sorted(
            data,
            key=lambda x: (
                AIAnalysisService._data_date(x) or datetime.min
            )
        )

        base_date = AIAnalysisService._data_date(sorted_data[0])
        if base_date is None:
            return []

        X = []
        y = []

        for item in sorted_data:
            date_value = AIAnalysisService._data_date(item)
            if date_value is None:
                continue

            day_index = (date_value - base_date).days
            X.append([day_index])
            y.append(float(item.get("engagement") or 0))

        if len(X) < 2:
            return []

        X = np.array(X)
        y = np.array(y)

        model = LinearRegression()
        model.fit(X, y)

        last_day = int(np.max(X[:, 0]))
        future_days = np.arange(
            last_day + 1,
            last_day + 31
        ).reshape(-1, 1)

        predictions = np.maximum(
            model.predict(future_days),
            0
        )

        return [
            {
                "day": index,
                "predicted_engagement": round(float(value), 2)
            }
            for index, value in enumerate(predictions, start=1)
        ]

    @staticmethod
    def forecast_per_content(data):
        groups = {}

        for item in data:
            content_type = item.get("media_type") or "UNKNOWN"
            groups.setdefault(content_type, []).append(item)

        result = {}

        for content_type, items in groups.items():
            if len(items) < 2:
                continue

            items = sorted(
                items,
                key=lambda x: (
                    AIAnalysisService._data_date(x) or datetime.min
                )
            )

            base_date = AIAnalysisService._data_date(items[0])
            if base_date is None:
                continue

            X = []
            y = []

            for item in items:
                date_value = AIAnalysisService._data_date(item)
                if date_value is None:
                    continue

                X.append([(date_value - base_date).days])
                y.append(float(item.get("engagement") or 0))

            if len(X) < 2:
                continue

            X = np.array(X)
            y = np.array(y)

            model = LinearRegression()
            model.fit(X, y)

            last_day = int(np.max(X[:, 0]))
            future_days = np.arange(
                last_day + 1,
                last_day + 31
            ).reshape(-1, 1)

            predictions = np.maximum(
                model.predict(future_days),
                0
            )

            result[content_type] = [
                round(float(value), 2)
                for value in predictions
            ]

        return result

    @staticmethod
    def predict_best_content(
        forecast_content
    ):
        if not forecast_content:
            return {
                "content_type": None,
                "average_prediction": 0
            }

        best_content = None
        best_value = -1

        for content_type, values in (
            forecast_content.items()
        ):

            if not values:
                continue

            average_value = (
                sum(values)
                / len(values)
            )

            if average_value > best_value:
                best_value = average_value
                best_content = content_type

        return {
            "content_type": best_content,
            "average_prediction": round(
                best_value,
                2
            )
        }

    @staticmethod
    def generate_strategy(
        best_content
    ):
        if not best_content:
            return [
                "Belum cukup data untuk membuat strategi."
            ]

        return [
            (
                f"Prioritaskan format "
                f"{best_content}."
            ),
            (
                "Gunakan konten dengan pola "
                "engagement terbaik sebagai referensi."
            ),
            (
                "Pertahankan konsistensi publikasi "
                "dan evaluasi performa secara berkala."
            )
        ]

    @staticmethod
    def save_clusters(cluster_results):
        """Simpan/update satu hasil cluster untuk setiap post."""
        if not cluster_results:
            return {"success": True, "saved": 0, "updated": 0}

        saved = 0
        updated = 0

        for item in cluster_results:
            post_id = item.get("id_posts")
            if not post_id:
                continue

            existing = (
                Clusters.query
                .filter_by(id_posts=post_id)
                .first()
            )

            values = {
                "cluster_label": item.get("cluster_label"),
                "performance_score": float(
                    item.get("engagement") or 0
                ),
                "created_at": datetime.now()
            }

            if existing:
                for key, value in values.items():
                    setattr(existing, key, value)
                updated += 1
            else:
                db.session.add(
                    Clusters(
                        id_posts=post_id,
                        **values
                    )
                )
                saved += 1

        return {
            "success": True,
            "saved": saved,
            "updated": updated
        }

    @staticmethod
    def save_forecast(data, forecast_results):
        """
        Simpan forecast 30 hari berdasarkan observasi terakhir.
        Kombinasi id_posts + forecast_date yang sudah ada akan di-update.
        """
        if not data or not forecast_results:
            return {"success": True, "saved": 0, "updated": 0}

        valid_items = [
            item for item in data
            if item.get("id_posts")
            and AIAnalysisService._data_date(item) is not None
        ]

        if not valid_items:
            return {
                "success": False,
                "saved": 0,
                "updated": 0,
                "message": "Tidak ada data valid untuk basis forecast."
            }

        latest_item = max(
            valid_items,
            key=lambda item: AIAnalysisService._data_date(item)
        )

        post_id = latest_item["id_posts"]
        base_date = AIAnalysisService._to_date(
            AIAnalysisService._data_date(latest_item)
        )

        if base_date is None:
            return {
                "success": False,
                "saved": 0,
                "updated": 0,
                "message": "Tanggal basis forecast tidak valid."
            }

        saved = 0
        updated = 0

        for item in forecast_results:
            try:
                day = int(item.get("day", 0))
                predicted = max(
                    float(item.get("predicted_engagement", 0) or 0),
                    0.0
                )
            except (TypeError, ValueError):
                continue

            if day < 1:
                continue

            forecast_date = base_date + timedelta(days=day)

            existing = (
                Forecast.query
                .filter_by(
                    id_posts=post_id,
                    forecast_date=forecast_date
                )
                .first()
            )

            if existing:
                existing.predicted_engagement = predicted
                existing.created_at = datetime.now()
                updated += 1
            else:
                db.session.add(
                    Forecast(
                        id_posts=post_id,
                        forecast_date=forecast_date,
                        predicted_engagement=predicted,
                        created_at=datetime.now()
                    )
                )
                saved += 1

        return {
            "success": True,
            "saved": saved,
            "updated": updated,
            "post_id": post_id,
            "base_date": base_date.isoformat()
        }

    @staticmethod
    def save_recommendation(
        ai_insight,
        strategy
    ):
        try:

            response = {
                "insight": ai_insight,
                "strategy": strategy
            }

            recommendation = Recommendations(
                prompt=(
                    "Analisis performa konten Instagram "
                    "dan berikan rekomendasi strategi."
                ),
                response=str(response),
                validation_score=0,
                validation_status="generated",
                generated_at=datetime.now()
            )

            db.session.add(
                recommendation
            )

            db.session.commit()

            return {
                "success": True,
                "id_rec": recommendation.id_rec
            }

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def analyze(
        month=None,
        year=None
    ):
        data = (
            AIAnalysisService
            .load_data(
                month=month,
                year=year
            )
        )

        if not data:
            return {
                "total_content": 0,
                "cluster": {
                    "cluster_count": 0,
                    "distribution": {},
                    "results": []
                },
                "cluster_summary": [],
                "ai_insight": {
                    "best_content": None,
                    "insight": "Data tidak ditemukan.",
                    "trend": "Stabil",
                    "prediction": None,
                    "strategy": []
                },
                "forecast": [],
                "forecast_per_content": {},
                "best_content_next_week": {
                    "content_type": None,
                    "average_prediction": 0
                },
                "strategy": [],
                "_raw_data": []
            }

        cluster_result = (
            AIAnalysisService
            .clustering(data)
        )

        cluster_summary = (
            AIAnalysisService
            .cluster_summary(
                cluster_result["results"]
            )
        )

        ai_insight = (
            AIAnalysisService
            .generate_ai_insight(
                data
            )
        )

        forecast = (
            AIAnalysisService
            .forecast_engagement(
                data
            )
        )

        forecast_content = (
            AIAnalysisService
            .forecast_per_content(
                data
            )
        )

        best_future = (
            AIAnalysisService
            .predict_best_content(
                forecast_content
            )
        )

        strategy = (
            AIAnalysisService
            .generate_strategy(
                best_future["content_type"]
            )
        )

        try:
            cluster_save_result = AIAnalysisService.save_clusters(
                cluster_result["results"]
            )

            forecast_save_result = AIAnalysisService.save_forecast(
                data,
                forecast
            )

            # Satu commit untuk cluster + forecast.
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

        return {
            "total_content": len(data),
            "cluster": cluster_result,
            "cluster_summary": cluster_summary,
            "cluster_save": cluster_save_result,
            "ai_insight": ai_insight,
            "forecast": forecast,
            "forecast_save": forecast_save_result,
            "forecast_per_content": forecast_content,
            "best_content_next_week": best_future,
            "strategy": strategy,
            "_raw_data": data
        }