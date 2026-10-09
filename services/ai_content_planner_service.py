from datetime import datetime, timedelta
import json
import os
import re
import time

from google import genai

from extensions import db

from models import (
    Recommendations,
    Content_Pillar,
    AIDAStage,
    ContentRecommendations,
    Forecast,
    Knowledge_Base,
    Embeddings
)

from services.knowledge_base_service import (
    KnowledgeBaseService
)

from services.ai_analysis_service import (
    AIAnalysisService
)


class AIContentPlannerService:

    MODEL_NAME = "gemini-3.6-flash"
    EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
    DEFAULT_DAYS = 30
    RAG_TOP_K = 5
    GEMINI_TIMEOUT_MS = 300000
    GEMINI_RETRIES = 3

    @staticmethod
    def get_client():

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY belum dikonfigurasi"
            )

        return genai.Client(
            api_key=api_key,
            http_options={
                "timeout": (
                    AIContentPlannerService
                    .GEMINI_TIMEOUT_MS
                )
            }
        )

    @staticmethod
    def generate_text(
        prompt
    ):

        client = (
            AIContentPlannerService
            .get_client()
        )

        print("")
        print(
            "============================================"
        )
        print(
            "GEMINI 3.6 FLASH - SINGLE REQUEST"
        )
        print(
            "============================================"
        )

        try:

            interaction = (
                client.interactions.create(
                    model=(
                        AIContentPlannerService
                        .MODEL_NAME
                    ),
                    input=prompt
                )
            )

            output = (
                getattr(
                    interaction,
                    "output_text",
                    None
                )
                or ""
            ).strip()

            if not output:

                raise RuntimeError(
                    "Gemini 3.6 Flash mengembalikan response kosong."
                )

            print(
                "GEMINI 3.6 FLASH RESPONSE: OK"
            )

            return output

        except Exception as e:

            print(
                "GEMINI 3.6 FLASH ERROR:",
                type(e).__name__,
                str(e)
            )

            raise RuntimeError(
                "Gemini 3.6 Flash gagal diakses: "
                f"{type(e).__name__}: {e}"
            ) from e

    @staticmethod
    def get_pillars():

        return (
            Content_Pillar.query
            .order_by(
                Content_Pillar.id_pillar.asc()
            )
            .all()
        )

    @staticmethod
    def get_aida_stages():

        return (
            AIDAStage.query
            .order_by(
                AIDAStage.id_aida.asc()
            )
            .all()
        )

    @staticmethod
    def get_forecasts(
        number_of_days=30
    ):

        return (
            Forecast.query
            .order_by(
                Forecast.forecast_date.asc()
            )
            .limit(number_of_days)
            .all()
        )

    @staticmethod
    def get_analysis_data():

        data = (
            AIAnalysisService
            .load_data()
        )

        if not data:
            return []

        return data

    @staticmethod
    def build_performance_context(data):

        if not data:
            return (
                "Tidak tersedia data performa Meta."
            )

        lines = []

        for item in data:

            lines.append(
                (
                    f"Post: "
                    f"{item.get('meta_post_id', '')}\n"
                    f"Caption: "
                    f"{item.get('caption', '')}\n"
                    f"Media Type: "
                    f"{item.get('media_type', '')}\n"
                    f"Media Product Type: "
                    f"{item.get('media_product_type', '')}\n"
                    f"Views: "
                    f"{item.get('views', 0)}\n"
                    f"Reach: "
                    f"{item.get('reach', 0)}\n"
                    f"Likes: "
                    f"{item.get('likes', 0)}\n"
                    f"Comments: "
                    f"{item.get('comments', 0)}\n"
                    f"Shares: "
                    f"{item.get('shares', 0)}\n"
                    f"Saves: "
                    f"{item.get('saves', 0)}\n"
                    f"Engagement: "
                    f"{item.get('engagement', 0)}"
                )
            )

        return "\n\n".join(lines)

    @staticmethod
    def get_content_type_summary(data):

        summary = {}

        for item in data:

            media_type = (
                item.get(
                    "media_type"
                )
                or "UNKNOWN"
            )

            engagement = float(
                item.get(
                    "engagement",
                    0
                )
                or 0
            )

            if media_type not in summary:

                summary[media_type] = {
                    "total": 0,
                    "count": 0
                }

            summary[media_type][
                "total"
            ] += engagement

            summary[media_type][
                "count"
            ] += 1

        result = {}

        for media_type, value in summary.items():

            average = (
                value["total"]
                / value["count"]
                if value["count"] > 0
                else 0
            )

            result[media_type] = {
                "total": value["total"],
                "count": value["count"],
                "average": round(
                    average,
                    2
                )
            }

        return result

    @staticmethod
    def get_best_content(data):

        if not data:
            return None

        return max(
            data,
            key=lambda x: float(
                x.get(
                    "engagement",
                    0
                )
                or 0
            )
        )

    @staticmethod
    def build_initial_prompt(
        data,
        number_of_days
    ):

        performance_context = (
            AIContentPlannerService
            .build_performance_context(
                data
            )
        )

        content_summary = (
            AIContentPlannerService
            .get_content_type_summary(
                data
            )
        )

        best_content = (
            AIContentPlannerService
            .get_best_content(
                data
            )
        )

        best_content_text = (
            "Tidak tersedia"
        )

        if best_content:

            best_content_text = (
                f"Post: "
                f"{best_content.get('meta_post_id', '')}\n"
                f"Caption: "
                f"{best_content.get('caption', '')}\n"
                f"Media: "
                f"{best_content.get('media_type', '')}\n"
                f"Engagement: "
                f"{best_content.get('engagement', 0)}"
            )

        return f"""
Anda adalah AI Content Planner
untuk sistem MAVis
(Meta Analytical Visual).

Buat rencana konten Instagram
untuk {number_of_days} hari.

Gunakan data performa Meta
sebagai dasar menentukan jenis
dan strategi konten.

Jangan mengarang angka performa.

Data performa:

{performance_context}

Ringkasan performa berdasarkan
jenis konten:

{json.dumps(
    content_summary,
    ensure_ascii=False,
    indent=2
)}

Konten dengan engagement
tertinggi:

{best_content_text}

Untuk setiap hari hasilkan:

- content_title
- content_description
- content_type
- objective

Buat ide yang bervariasi.

Jangan hanya mengganti nomor
pada judul.

Gunakan bahasa Indonesia.

Output HARUS berupa JSON valid.

Format:

[
    {{
        "day": 1,
        "content_title": "...",
        "content_description": "...",
        "content_type": "VIDEO",
        "objective": "..."
    }}
]

Jumlah item HARUS tepat
{number_of_days}.
"""

    @staticmethod
    def generate_initial_ideas(
        data,
        number_of_days
    ):

        prompt = (
            AIContentPlannerService
            .build_initial_prompt(
                data=data,
                number_of_days=number_of_days
            )
        )

        output = (
            AIContentPlannerService
            .generate_text(
                prompt
            )
        )

        result = (
            AIContentPlannerService
            .parse_json_output(
                output
            )
        )

        if not isinstance(
            result,
            list
        ):
            raise ValueError(
                "Response Gemini harus berupa array"
            )

        if len(result) < number_of_days:

            raise ValueError(
                (
                    "Gemini hanya menghasilkan "
                    f"{len(result)} ide dari "
                    f"{number_of_days} yang diminta"
                )
            )

        return result[:number_of_days]

    @staticmethod
    def parse_json_output(output):

        if not output:
            raise ValueError(
                "Response Gemini kosong"
            )

        cleaned = output.strip()

        cleaned = re.sub(
            r"^```json\s*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = re.sub(
            r"^```\s*",
            "",
            cleaned
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned
        )

        cleaned = cleaned.strip()

        try:

            return json.loads(
                cleaned
            )

        except json.JSONDecodeError:

            match = re.search(
                r"\[.*\]",
                cleaned,
                re.DOTALL
            )

            if match:

                return json.loads(
                    match.group(0)
                )

            object_match = re.search(
                r"\{.*\}",
                cleaned,
                re.DOTALL
            )

            if object_match:

                return [
                    json.loads(
                        object_match.group(0)
                    )
                ]

            raise ValueError(
                "Response Gemini bukan JSON valid"
            )

    @staticmethod
    def build_rag_query(ideas):

        parts = []

        for index, idea in enumerate(
            ideas
        ):

            parts.append(
                (
                    f"Ide {index + 1}: "
                    f"{idea.get('content_title', '')}. "
                    f"{idea.get('content_description', '')}. "
                    f"Jenis: "
                    f"{idea.get('content_type', '')}. "
                    f"Tujuan: "
                    f"{idea.get('objective', '')}."
                )
            )

        return (
            "Strategi konten Instagram "
            "untuk meningkatkan engagement "
            "berdasarkan ide berikut:\n"
            + "\n".join(parts)
        )

    @staticmethod
    def retrieve_rag(
        ideas,
        top_k=5,
        instagram_user_id=None
    ):

        query = (
            AIContentPlannerService
            .build_rag_query(
                ideas
            )
        )

        results = (
            KnowledgeBaseService
            .search(
                query=query,
                top_k=top_k,
                instagram_user_id=instagram_user_id
            )
        )

        context_parts = []

        sources = []

        for item in results:

            context_parts.append(
                (
                    f"Judul: "
                    f"{item['title']}\n"
                    f"Isi: "
                    f"{item['content']}\n"
                    f"Similarity: "
                    f"{item['similarity']}"
                )
            )

            sources.append({
                "id_kb": item["id_kb"],
                "title": item["title"],
                "similarity": item[
                    "similarity"
                ]
            })

        return {
            "query": query,
            "context": (
                "\n\n".join(
                    context_parts
                )
            ),
            "sources": sources
        }

    @staticmethod
    def build_final_prompt(
        ideas,
        rag_result,
        pillars,
        aida_stages,
        number_of_days
    ):

        pillar_context = []

        for pillar in pillars:

            pillar_context.append({
                "id_pillar": (
                    pillar.id_pillar
                ),
                "pillar_name": (
                    pillar.pillar_name
                ),
                "description": (
                    pillar.description
                )
            })

        aida_context = []

        for aida in aida_stages:

            aida_context.append({
                "id_aida": (
                    aida.id_aida
                ),
                "stage_name": (
                    aida.stage_name
                ),
                "description": (
                    aida.description
                )
            })

        return f"""
Anda adalah AI Content Planner
untuk sistem MAVis.

Anda menerima ide awal konten
berdasarkan performa Meta.

Anda juga menerima informasi
Knowledge Base yang ditemukan
menggunakan RAG.

Gunakan informasi Knowledge Base
sebagai referensi untuk
menyempurnakan ide konten.

Knowledge Base hasil RAG:

{rag_result["context"]}

Ide awal dari Gemini:

{json.dumps(
    ideas,
    ensure_ascii=False,
    indent=2
)}

Content Pillar yang tersedia:

{json.dumps(
    pillar_context,
    ensure_ascii=False,
    indent=2
)}

AIDA Stage yang tersedia:

{json.dumps(
    aida_context,
    ensure_ascii=False,
    indent=2
)}

Buat hasil final untuk
{number_of_days} hari.

Setiap item wajib memiliki:

- day
- content_title
- content_description
- content_type
- objective
- id_pillar
- id_aida

Gunakan hanya ID yang tersedia.

Jangan membuat ID baru.

Buat judul dan deskripsi
yang spesifik dan bervariasi.

Jangan hanya mengganti angka
pada judul.

Jangan mengarang fakta yang
seolah-olah berasal dari
Knowledge Base.

Output HARUS berupa JSON valid
tanpa markdown.

Format:

[
    {{
        "day": 1,
        "content_title": "...",
        "content_description": "...",
        "content_type": "VIDEO",
        "objective": "...",
        "id_pillar": 1,
        "id_aida": 1
    }}
]

Jumlah item HARUS tepat
{number_of_days}.
"""

    @staticmethod
    def generate_final_ideas(
        ideas,
        rag_result,
        pillars,
        aida_stages,
        number_of_days
    ):

        prompt = (
            AIContentPlannerService
            .build_final_prompt(
                ideas=ideas,
                rag_result=rag_result,
                pillars=pillars,
                aida_stages=aida_stages,
                number_of_days=number_of_days
            )
        )

        output = (
            AIContentPlannerService
            .generate_text(
                prompt
            )
        )

        result = (
            AIContentPlannerService
            .parse_json_output(
                output
            )
        )

        if not isinstance(
            result,
            list
        ):
            raise ValueError(
                "Response Gemini final harus berupa array"
            )

        if len(result) < number_of_days:

            raise ValueError(
                (
                    "Gemini final hanya menghasilkan "
                    f"{len(result)} item dari "
                    f"{number_of_days} yang diminta"
                )
            )

        return result[:number_of_days]

    @staticmethod
    def get_pillar_by_id(
        pillars,
        id_pillar
    ):

        for pillar in pillars:

            if pillar.id_pillar == id_pillar:
                return pillar

        return None

    @staticmethod
    def get_aida_by_id(
        aida_stages,
        id_aida
    ):

        for aida in aida_stages:

            if aida.id_aida == id_aida:
                return aida

        return None

    @staticmethod
    def build_plan(
        final_ideas,
        pillars,
        aida_stages,
        forecasts,
        number_of_days
    ):

        plan = []

        base_date = (
            datetime.now().date()
        )

        for index in range(
            number_of_days
        ):

            idea = final_ideas[index]

            id_pillar = idea.get(
                "id_pillar"
            )

            id_aida = idea.get(
                "id_aida"
            )

            pillar = (
                AIContentPlannerService
                .get_pillar_by_id(
                    pillars,
                    id_pillar
                )
            )

            aida = (
                AIContentPlannerService
                .get_aida_by_id(
                    aida_stages,
                    id_aida
                )
            )

            if not pillar:

                pillar = pillars[
                    index % len(pillars)
                ]

            if not aida:

                aida = aida_stages[
                    index % len(aida_stages)
                ]

            posting_date = (
                base_date
                + timedelta(
                    days=index
                )
            )

            predicted_engagement = 0

            if index < len(forecasts):

                forecast = forecasts[index]

                if forecast.forecast_date:

                    posting_date = (
                        forecast.forecast_date
                    )

                predicted_engagement = (
                    forecast.predicted_engagement
                    or 0
                )

            if hasattr(
                posting_date,
                "isoformat"
            ):

                posting_date_string = (
                    posting_date.isoformat()
                )

            else:

                posting_date_string = (
                    str(posting_date)
                )

            plan.append({
                "id_aida": (
                    aida.id_aida
                ),
                "id_pillar": (
                    pillar.id_pillar
                ),
                "content_title": (
                    idea.get(
                        "content_title",
                        "Rekomendasi Konten"
                    )
                ),
                "content_description": (
                    idea.get(
                        "content_description",
                        ""
                    )
                ),
                "content_type": (
                    idea.get(
                        "content_type",
                        "IMAGE"
                    )
                ),
                "objective": (
                    idea.get(
                        "objective",
                        ""
                    )
                ),
                "posting_date": (
                    posting_date_string
                ),
                "predicted_engagement": (
                    float(
                        predicted_engagement
                    )
                ),
                "aida_stage": (
                    aida.stage_name
                ),
                "content_pillar": (
                    pillar.pillar_name
                )
            })

        return plan

    @staticmethod
    def save_recommendation(
        prompt,
        response
    ):

        try:

            recommendation = Recommendations(
                prompt=prompt,
                response=json.dumps(
                    response,
                    ensure_ascii=False
                ),
                validation_score=0,
                validation_status="generated",
                generated_at=datetime.now()
            )

            db.session.add(
                recommendation
            )

            db.session.flush()

            return recommendation

        except Exception:

            db.session.rollback()
            raise

    @staticmethod
    def save_plan(
        plan,
        recommendation
    ):

        if not recommendation:

            raise ValueError(
                "Recommendation belum tersedia"
            )

        saved = 0
        updated = 0

        try:

            for item in plan:

                posting_date = (
                    item["posting_date"]
                )

                if isinstance(
                    posting_date,
                    str
                ):

                    posting_date = (
                        datetime.strptime(
                            posting_date,
                            "%Y-%m-%d"
                        ).date()
                    )

                existing = (
                    ContentRecommendations.query
                    .filter_by(
                        id_rec=(
                            recommendation.id_rec
                        ),
                        posting_date=(
                            posting_date
                        )
                    )
                    .first()
                )

                if existing:

                    existing.id_aida = (
                        item["id_aida"]
                    )

                    existing.id_pillar = (
                        item["id_pillar"]
                    )

                    existing.content_title = (
                        item["content_title"]
                    )

                    existing.posting_date = (
                        posting_date
                    )

                    existing.predicted_engagement = (
                        item[
                            "predicted_engagement"
                        ]
                    )

                    existing.created_at = (
                        datetime.now()
                    )

                    updated += 1

                else:

                    content_recommendation = (
                        ContentRecommendations(
                            id_rec=(
                                recommendation.id_rec
                            ),
                            id_aida=(
                                item["id_aida"]
                            ),
                            id_pillar=(
                                item["id_pillar"]
                            ),
                            content_title=(
                                item["content_title"]
                            ),
                            posting_date=(
                                posting_date
                            ),
                            predicted_engagement=(
                                item[
                                    "predicted_engagement"
                                ]
                            ),
                            created_at=(
                                datetime.now()
                            )
                        )
                    )

                    db.session.add(
                        content_recommendation
                    )

                    saved += 1

            db.session.commit()

            return {
                "success": True,
                "saved": saved,
                "updated": updated
            }

        except Exception:

            db.session.rollback()
            raise


    @staticmethod
    def clear_content_plan_history():

        """
        Menghapus riwayat Content Planner sebelumnya.

        Urutan:
        1. Hapus ContentRecommendations terlebih dahulu
           karena tabel ini mereferensikan Recommendations.
        2. Hapus Recommendations agar tidak meninggalkan
           data recommendation yang sudah tidak digunakan.

        Cleanup dilakukan hanya setelah proses AI berhasil
        menghasilkan plan baru, tepat sebelum data baru
        disimpan.
        """

        try:

            old_content_plans = (
                ContentRecommendations.query
                .all()
            )

            deleted_plans = len(
                old_content_plans
            )

            for item in old_content_plans:

                db.session.delete(
                    item
                )

            db.session.flush()


            old_recommendations = (
                Recommendations.query
                .all()
            )

            deleted_recommendations = len(
                old_recommendations
            )

            for item in old_recommendations:

                db.session.delete(
                    item
                )

            db.session.flush()


            print("")
            print(
                "CONTENT PLANNER HISTORY CLEARED"
            )
            print(
                "OLD CONTENT PLANS:",
                deleted_plans
            )
            print(
                "OLD RECOMMENDATIONS:",
                deleted_recommendations
            )
            print("")


            return {
                "success": True,
                "deleted_content_plans":
                    deleted_plans,
                "deleted_recommendations":
                    deleted_recommendations
            }


        except Exception:

            db.session.rollback()

            raise


    @staticmethod
    def build_unified_prompt(
        data,
        rag_result,
        pillars,
        aida_stages,
        forecasts,
        number_of_days
    ):

        performance_context = (
            AIContentPlannerService
            .build_performance_context(
                data
            )
        )

        content_summary = (
            AIContentPlannerService
            .get_content_type_summary(
                data
            )
        )

        pillar_context = []

        for pillar in pillars:

            pillar_context.append({
                "id_pillar":
                    pillar.id_pillar,

                "pillar_name":
                    pillar.pillar_name,

                "description":
                    pillar.description
            })


        aida_context = []

        for aida in aida_stages:

            aida_context.append({
                "id_aida":
                    aida.id_aida,

                "stage_name":
                    aida.stage_name,

                "description":
                    aida.description
            })


        forecast_context = []

        for forecast in forecasts:

            forecast_context.append({

                "forecast_date":
                    (
                        forecast.forecast_date.isoformat()
                        if hasattr(
                            forecast.forecast_date,
                            "isoformat"
                        )
                        else str(
                            forecast.forecast_date
                        )
                    ),

                "predicted_engagement":
                    float(
                        forecast.predicted_engagement
                        or 0
                    )

            })


        rag_context = (
            rag_result.get(
                "context",
                ""
            )
            or
            "Tidak ada dokumen Knowledge Base yang relevan."
        )


        return f"""
Anda adalah AI Content Planner untuk sistem MAVis.

Tugas Anda adalah membuat Content Planner Instagram
untuk perusahaan berdasarkan:
1. data performa Instagram/Meta,
2. Knowledge Base perusahaan,
3. Content Pillar,
4. AIDA Stage,
5. forecast engagement.

PERUSAHAAN:
Gunakan hanya informasi yang diberikan oleh Knowledge Base.
Jangan mengarang nama layanan, lokasi, klien, angka,
tahun berdiri, atau fakta perusahaan yang tidak tersedia.

KNOWLEDGE BASE HASIL SEMANTIC SEARCH:
{rag_context}

DATA PERFORMA META:
{performance_context}

RINGKASAN PERFORMA JENIS KONTEN:
{json.dumps(
    content_summary,
    ensure_ascii=False,
    indent=2
)}

CONTENT PILLAR:
{json.dumps(
    pillar_context,
    ensure_ascii=False,
    indent=2
)}

AIDA STAGE:
{json.dumps(
    aida_context,
    ensure_ascii=False,
    indent=2
)}

FORECAST:
{json.dumps(
    forecast_context,
    ensure_ascii=False,
    indent=2
)}

BUAT RENCANA KONTEN UNTUK {number_of_days} HARI.

ATURAN:
- Tepat {number_of_days} item.
- day dimulai dari 1 sampai {number_of_days}.
- Setiap item memiliki:
  day,
  content_title,
  content_description,
  content_type,
  objective,
  id_pillar,
  id_aida.
- Gunakan hanya id_pillar dan id_aida yang tersedia.
- Variasikan topik dan format konten.
- Jangan hanya mengganti nomor/judul.
- Sesuaikan konten dengan jasa konstruksi,
  studio arsitek, dan interior rumah custom
  hanya jika didukung oleh Knowledge Base.
- Gunakan insight performa Meta untuk memilih
  format dan pendekatan konten.
- Gunakan forecast sebagai pertimbangan,
  bukan sebagai fakta yang harus ditampilkan ke publik.
- Gunakan bahasa Indonesia.
- Jangan membuat klaim perusahaan yang tidak ada
  di Knowledge Base.
- Jangan memasukkan markdown.
- Output HARUS berupa JSON valid berupa array.
- Tidak boleh ada teks sebelum atau sesudah JSON.

FORMAT:
[
  {{
    "day": 1,
    "content_title": "...",
    "content_description": "...",
    "content_type": "VIDEO",
    "objective": "...",
    "id_pillar": 1,
    "id_aida": 1
  }}
]

Jumlah item HARUS tepat {number_of_days}.
"""


    @staticmethod
    def get_rag_for_company(
        data,
        instagram_user_id=None
    ):

        # =================================================
        # RAG LOKAL — TANPA REQUEST GEMINI
        # =================================================
        #
        # Implementasi dilakukan langsung di service ini
        # supaya aman terhadap numpy ndarray dari
        # SentenceTransformer. Query vector dikonversi
        # menjadi list Python sebelum cosine similarity,
        # sehingga tidak memicu:
        #
        # "The truth value of an array with more than one
        # element is ambiguous"
        # =================================================

        if not instagram_user_id:

            return {
                "query":
                    "",
                "context":
                    "",
                "sources":
                    []
            }


        content_summary = (
            AIContentPlannerService
            .get_content_type_summary(
                data
            )
        )


        query = (
            "Profil perusahaan dan strategi konten Instagram "
            "untuk perusahaan jasa konstruksi, studio arsitek, "
            "dan interior rumah custom. "
            "Gunakan informasi tentang layanan, target klien, "
            "gaya komunikasi brand, konten edukasi, portofolio, "
            "dan strategi pemasaran. "
            f"Ringkasan jenis konten: "
            f"{json.dumps(content_summary, ensure_ascii=False)}"
        )


        # -------------------------------------------------
        # EMBEDDING QUERY
        # -------------------------------------------------

        model = (
            KnowledgeBaseService
            .get_model()
        )


        query_vector = model.encode(
            query,
            normalize_embeddings=True
        )


        # Numpy ndarray -> Python list
        if hasattr(
            query_vector,
            "tolist"
        ):

            query_vector = (
                query_vector.tolist()
            )


        # -------------------------------------------------
        # AMBIL KNOWLEDGE BASE MILIK AKUN AKTIF SAJA
        # -------------------------------------------------

        knowledge_bases = (

            Knowledge_Base.query

            .filter(
                Knowledge_Base
                .instagram_user_id
                ==
                str(
                    instagram_user_id
                )
            )

            .all()

        )


        scored = []


        for kb in knowledge_bases:

            embedding = (

                Embeddings.query

                .filter_by(
                    id_kb=
                        kb.id_kb
                )

                .order_by(
                    Embeddings.created_at.desc()
                )

                .first()

            )


            if embedding is None:

                continue


            try:

                vector = json.loads(
                    embedding.vector_data
                )

            except (
                TypeError,
                json.JSONDecodeError
            ):

                continue


            if not isinstance(
                vector,
                list
            ):

                if hasattr(
                    vector,
                    "tolist"
                ):

                    vector = vector.tolist()

                else:

                    continue


            if len(vector) == 0:

                continue


            if len(vector) != len(
                query_vector
            ):

                continue


            try:

                score = (
                    KnowledgeBaseService
                    .cosine_similarity(
                        query_vector,
                        vector
                    )
                )

            except Exception as e:

                print(
                    "RAG COSINE ERROR:",
                    repr(e)
                )

                continue


            scored.append({

                "id_kb":
                    kb.id_kb,

                "title":
                    kb.title,

                "content":
                    kb.content,

                "source_type":
                    kb.source_type,

                "instagram_user_id":
                    kb.instagram_user_id,

                "similarity":
                    round(
                        float(score),
                        6
                    )

            })


        scored.sort(

            key=lambda item:
                item["similarity"],

            reverse=True

        )


        results = scored[
            :AIContentPlannerService.RAG_TOP_K
        ]


        context_parts = []
        sources = []


        for item in results:

            context_parts.append(

                (
                    f"Judul: "
                    f"{item['title']}\n"

                    f"Isi: "
                    f"{item['content']}\n"

                    f"Similarity: "
                    f"{item['similarity']}"
                )

            )


            sources.append({

                "id_kb":
                    item["id_kb"],

                "title":
                    item["title"],

                "similarity":
                    item["similarity"]

            })


        print("")
        print(
            "RAG KNOWLEDGE BASE"
        )
        print(
            "INSTAGRAM USER ID:",
            instagram_user_id
        )
        print(
            "KB TERSEDIA:",
            len(knowledge_bases)
        )
        print(
            "KB TERPILIH:",
            len(results)
        )
        print("")


        return {

            "query":
                query,

            "context":
                "\n\n".join(
                    context_parts
                ),

            "sources":
                sources

        }

    @staticmethod
    def parse_planner_output(
        output,
        number_of_days
    ):

        result = (
            AIContentPlannerService
            .parse_json_output(
                output
            )
        )

        if not isinstance(
            result,
            list
        ):

            raise ValueError(
                "Response Content Planner harus berupa array JSON."
            )

        if len(result) < number_of_days:

            raise ValueError(
                (
                    "Gemini hanya menghasilkan "
                    f"{len(result)} item dari "
                    f"{number_of_days} yang diminta."
                )
            )

        result = result[
            :number_of_days
        ]

        required_fields = [
            "day",
            "content_title",
            "content_description",
            "content_type",
            "objective",
            "id_pillar",
            "id_aida"
        ]

        normalized = []

        for index, item in enumerate(result):

            if not isinstance(
                item,
                dict
            ):

                raise ValueError(
                    f"Item hari {index + 1} bukan object JSON."
                )

            normalized_item = {
                "day":
                    index + 1,

                "content_title":
                    str(
                        item.get(
                            "content_title",
                            ""
                        )
                    ).strip(),

                "content_description":
                    str(
                        item.get(
                            "content_description",
                            ""
                        )
                    ).strip(),

                "content_type":
                    str(
                        item.get(
                            "content_type",
                            "IMAGE"
                        )
                    ).strip().upper(),

                "objective":
                    str(
                        item.get(
                            "objective",
                            ""
                        )
                    ).strip(),

                "id_pillar":
                    item.get(
                        "id_pillar"
                    ),

                "id_aida":
                    item.get(
                        "id_aida"
                    )
            }

            if not normalized_item[
                "content_title"
            ]:

                raise ValueError(
                    f"Judul konten hari {index + 1} kosong."
                )

            if not normalized_item[
                "content_description"
            ]:

                raise ValueError(
                    (
                        "Deskripsi konten hari "
                        f"{index + 1} kosong."
                    )
                )

            normalized.append(
                normalized_item
            )

        return normalized


    @staticmethod
    def generate_plan(
        number_of_days=30,
        instagram_user_id=None
    ):

        if number_of_days < 1:

            raise ValueError(
                "Jumlah hari harus lebih dari 0"
            )

        if number_of_days > 30:

            number_of_days = 30

        if not instagram_user_id:

            raise ValueError(
                "Instagram User ID akun aktif belum tersedia."
            )

        instagram_user_id = str(
            instagram_user_id
        ).strip()


        print("")
        print(
            "============================================"
        )
        print(
            "AI CONTENT PLANNER - SINGLE GEMINI REQUEST"
        )
        print(
            "INSTAGRAM USER ID:",
            instagram_user_id
        )
        print(
            "NUMBER OF DAYS:",
            number_of_days
        )
        print(
            "============================================"
        )


        # =================================================
        # 1. DATA PERFORMA
        # =================================================

        data = (
            AIContentPlannerService
            .get_analysis_data()
        )

        if not data:

            raise ValueError(
                "Data performa Meta belum tersedia"
            )


        # =================================================
        # 2. CONTENT PILLAR
        # =================================================

        pillars = (
            AIContentPlannerService
            .get_pillars()
        )

        if not pillars:

            raise ValueError(
                "Content Pillar belum tersedia"
            )


        # =================================================
        # 3. AIDA
        # =================================================

        aida_stages = (
            AIContentPlannerService
            .get_aida_stages()
        )

        if not aida_stages:

            raise ValueError(
                "AIDA Stage belum tersedia"
            )


        # =================================================
        # 4. FORECAST
        # =================================================

        forecasts = (
            AIContentPlannerService
            .get_forecasts(
                number_of_days
            )
        )

        if len(forecasts) < number_of_days:

            raise ValueError(
                (
                    f"Forecast belum tersedia "
                    f"untuk {number_of_days} hari"
                )
            )


        # =================================================
        # 5. RAG LOCAL — TANPA GEMINI
        # =================================================

        rag_result = (
            AIContentPlannerService
            .get_rag_for_company(
                data=data,
                instagram_user_id=instagram_user_id
            )
        )


        # =================================================
        # 6. SATU-SATUNYA REQUEST GEMINI
        # =================================================

        prompt = (
            AIContentPlannerService
            .build_unified_prompt(
                data=data,
                rag_result=rag_result,
                pillars=pillars,
                aida_stages=aida_stages,
                forecasts=forecasts,
                number_of_days=number_of_days
            )
        )

        output = (
            AIContentPlannerService
            .generate_text(
                prompt
            )
        )


        final_ideas = (
            AIContentPlannerService
            .parse_planner_output(
                output=output,
                number_of_days=number_of_days
            )
        )


        # =================================================
        # 7. BUILD PLAN LOCAL
        # =================================================

        plan = (
            AIContentPlannerService
            .build_plan(
                final_ideas=final_ideas,
                pillars=pillars,
                aida_stages=aida_stages,
                forecasts=forecasts,
                number_of_days=number_of_days
            )
        )


        # =================================================
        # 8. HAPUS RIWAYAT CONTENT PLANNER LAMA
        # =================================================
        #
        # Cleanup dilakukan SETELAH Gemini berhasil dan plan
        # baru sudah terbentuk. Dengan begitu, kalau Gemini
        # gagal, plan lama tetap aman.
        # =================================================

        history_cleanup = (
            AIContentPlannerService
            .clear_content_plan_history()
        )


        # =================================================
        # 9. SAVE RECOMMENDATION
        # =================================================

        recommendation_prompt = (
            "AI Content Planner MAVis menggunakan "
            "satu request Gemini 3.6 Flash untuk menghasilkan "
            f"rencana konten {number_of_days} hari, dengan "
            "Knowledge Base perusahaan sebagai konteks RAG "
            "lokal menggunakan "
            "all-MiniLM-L6-v2."
        )


        recommendation_response = {

            "model":
                AIContentPlannerService
                .MODEL_NAME,

            "embedding_model":
                AIContentPlannerService
                .EMBEDDING_MODEL_NAME,

            "number_of_days":
                number_of_days,

            "instagram_user_id":
                instagram_user_id,

            "rag":
                {
                    "query":
                        rag_result["query"],

                    "sources":
                        rag_result["sources"]
                },

            "final_ideas":
                final_ideas,

            "plan":
                plan

        }


        recommendation = (
            AIContentPlannerService
            .save_recommendation(
                prompt=
                    recommendation_prompt,

                response=
                    recommendation_response
            )
        )


        # =================================================
        # 9. SAVE CONTENT PLAN
        # =================================================

        saved = (
            AIContentPlannerService
            .save_plan(
                plan=plan,
                recommendation=recommendation
            )
        )


        return {

            "instagram_user_id":
                instagram_user_id,

            "recommendation": {

                "id_rec":
                    recommendation.id_rec,

                "model":
                    AIContentPlannerService
                    .MODEL_NAME,

                "embedding_model":
                    AIContentPlannerService
                    .EMBEDDING_MODEL_NAME,

                "rag_sources":
                    rag_result["sources"]

            },

            "plan":
                plan,

            "saved":
                saved

        }


    @staticmethod
    def get_all():

        results = (
            ContentRecommendations.query
            .order_by(
                ContentRecommendations
                .posting_date.asc()
            )
            .all()
        )

        data = []

        for item in results:

            data.append({
                "id_cr": item.id_cr,
                "id_rec": item.id_rec,
                "id_aida": item.id_aida,
                "id_pillar": item.id_pillar,
                "content_title": (
                    item.content_title
                ),
                "posting_date": (
                    item.posting_date
                ),
                "predicted_engagement": (
                    item.predicted_engagement
                ),
                "created_at": (
                    item.created_at
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

        return data

    @staticmethod
    def get_by_id(id_cr):

        item = (
            ContentRecommendations.query
            .filter_by(
                id_cr=id_cr
            )
            .first()
        )

        if not item:
            return None

        return {
            "id_cr": item.id_cr,
            "id_rec": item.id_rec,
            "id_aida": item.id_aida,
            "id_pillar": item.id_pillar,
            "content_title": (
                item.content_title
            ),
            "posting_date": (
                item.posting_date
            ),
            "predicted_engagement": (
                item.predicted_engagement
            ),
            "created_at": (
                item.created_at
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
        }