from datetime import datetime
import json

from flask import session
from sentence_transformers import SentenceTransformer

from extensions import db
from models import Knowledge_Base, Embeddings


class KnowledgeBaseService:

    MODEL_NAME = "all-MiniLM-L6-v2"

    @staticmethod
    def get_active_instagram_user_id(instagram_user_id=None):

        # Prioritas ID akun dari frontend yang sebelumnya diverifikasi
        # melalui endpoint Meta status.
        if instagram_user_id:

            value = str(instagram_user_id).strip()

            if value:
                return value

        # Fallback untuk request yang berada pada host/session Flask Meta.
        user_id = (
            session.get("meta_user_id")
            or session.get("meta_account_id")
        )

        if user_id:
            return str(user_id)

        raise ValueError(
            "Akun Instagram aktif tidak ditemukan. "
            "Hubungkan akun Instagram terlebih dahulu."
        )

    @staticmethod
    def get_model():

        return SentenceTransformer(
            KnowledgeBaseService.MODEL_NAME
        )

    @staticmethod
    def create(
        title,
        content,
        source_type="manual",
        instagram_user_id=None
    ):

        title = str(title or "").strip()
        content = str(content or "").strip()
        source_type = str(source_type or "manual").strip()

        if not title:
            raise ValueError(
                "Title knowledge base wajib diisi."
            )

        if not content:
            raise ValueError(
                "Content knowledge base wajib diisi."
            )

        active_user_id = (
            KnowledgeBaseService
            .get_active_instagram_user_id(
                instagram_user_id
            )
        )

        try:

            knowledge_base = Knowledge_Base(
                title=title,
                content=content,
                source_type=source_type or "manual",
                instagram_user_id=active_user_id,
                created_at=datetime.now()
            )

            db.session.add(
                knowledge_base
            )

            db.session.flush()

            return knowledge_base

        except Exception:

            db.session.rollback()
            raise

    @staticmethod
    def generate_embedding(content):

        if not content:
            raise ValueError(
                "Content embedding tidak boleh kosong."
            )

        model = (
            KnowledgeBaseService
            .get_model()
        )

        vector = model.encode(
            content,
            normalize_embeddings=True
        )

        return vector.tolist()

    @staticmethod
    def create_embedding(knowledge_base):

        if not knowledge_base:
            raise ValueError(
                "Knowledge Base tidak ditemukan."
            )

        vector = (
            KnowledgeBaseService
            .generate_embedding(
                knowledge_base.content
            )
        )

        embedding = Embeddings(
            id_kb=knowledge_base.id_kb,
            vector_data=json.dumps(vector),
            model_name=KnowledgeBaseService.MODEL_NAME,
            created_at=datetime.now()
        )

        db.session.add(
            embedding
        )

        return embedding

    @staticmethod
    def create_with_embedding(
        title,
        content,
        source_type="manual",
        instagram_user_id=None
    ):

        try:

            knowledge_base = (
                KnowledgeBaseService
                .create(
                    title=title,
                    content=content,
                    source_type=source_type,
                    instagram_user_id=instagram_user_id
                )
            )

            embedding = (
                KnowledgeBaseService
                .create_embedding(
                    knowledge_base
                )
            )

            db.session.commit()

            return {
                "success": True,
                "knowledge_base": {
                    "id_kb": knowledge_base.id_kb,
                    "title": knowledge_base.title,
                    "content": knowledge_base.content,
                    "source_type": knowledge_base.source_type,
                    "instagram_user_id":
                        knowledge_base.instagram_user_id,
                    "created_at": knowledge_base.created_at
                },
                "embedding": {
                    "id_embeddings":
                        embedding.id_embeddings,
                    "model_name":
                        embedding.model_name,
                    "dimension":
                        len(
                            json.loads(
                                embedding.vector_data
                            )
                        )
                }
            }

        except Exception:

            db.session.rollback()
            raise

    @staticmethod
    def get_all(instagram_user_id=None):

        active_user_id = (
            KnowledgeBaseService
            .get_active_instagram_user_id(
                instagram_user_id
            )
        )

        data = (
            Knowledge_Base.query
            .filter(
                Knowledge_Base.instagram_user_id
                == active_user_id
            )
            .order_by(
                Knowledge_Base.created_at.desc()
            )
            .all()
        )

        result = []

        for item in data:

            embedding = (
                Embeddings.query
                .filter_by(
                    id_kb=item.id_kb
                )
                .order_by(
                    Embeddings.created_at.desc()
                )
                .first()
            )

            result.append({
                "id_kb": item.id_kb,
                "title": item.title,
                "content": item.content,
                "source_type": item.source_type,
                "instagram_user_id":
                    item.instagram_user_id,
                "created_at": item.created_at,
                "embedding":
                    (
                        {
                            "id_embeddings":
                                embedding.id_embeddings,
                            "model_name":
                                embedding.model_name,
                            "created_at":
                                embedding.created_at
                        }
                        if embedding
                        else None
                    )
            })

        return result

    @staticmethod
    def get_by_id(
        id_kb,
        instagram_user_id=None
    ):

        active_user_id = (
            KnowledgeBaseService
            .get_active_instagram_user_id(
                instagram_user_id
            )
        )

        item = (
            Knowledge_Base.query
            .filter(
                Knowledge_Base.id_kb == id_kb,
                Knowledge_Base.instagram_user_id
                == active_user_id
            )
            .first()
        )

        if not item:
            return None

        return {
            "id_kb": item.id_kb,
            "title": item.title,
            "content": item.content,
            "source_type": item.source_type,
            "instagram_user_id":
                item.instagram_user_id,
            "created_at": item.created_at
        }

    @staticmethod
    def get_embedding(
        id_kb,
        instagram_user_id=None
    ):

        item = (
            KnowledgeBaseService
            .get_by_id(
                id_kb,
                instagram_user_id
            )
        )

        if not item:
            return None

        embedding = (
            Embeddings.query
            .filter_by(
                id_kb=id_kb
            )
            .order_by(
                Embeddings.created_at.desc()
            )
            .first()
        )

        if not embedding:
            return None

        try:
            vector = json.loads(
                embedding.vector_data
            )
        except (
            TypeError,
            json.JSONDecodeError
        ):
            vector = []

        return {
            "id_embeddings":
                embedding.id_embeddings,
            "id_kb":
                embedding.id_kb,
            "vector_data":
                vector,
            "model_name":
                embedding.model_name,
            "created_at":
                embedding.created_at
        }

    @staticmethod
    def search(
        query,
        top_k=5,
        instagram_user_id=None
    ):

        query = str(query or "").strip()

        if not query:
            return []

        active_user_id = (
            KnowledgeBaseService
            .get_active_instagram_user_id(
                instagram_user_id
            )
        )

        try:
            top_k = int(top_k)
        except (
            TypeError,
            ValueError
        ):
            top_k = 5

        if top_k <= 0:
            top_k = 5

        model = (
            KnowledgeBaseService
            .get_model()
        )

        query_vector = model.encode(
            query,
            normalize_embeddings=True
        )

        knowledge_bases = (
            Knowledge_Base.query
            .filter(
                Knowledge_Base.instagram_user_id
                == active_user_id
            )
            .all()
        )

        results = []

        for kb in knowledge_bases:

            embedding = (
                Embeddings.query
                .filter_by(
                    id_kb=kb.id_kb
                )
                .order_by(
                    Embeddings.created_at.desc()
                )
                .first()
            )

            if not embedding:
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

            if not vector:
                continue

            score = (
                KnowledgeBaseService
                .cosine_similarity(
                    query_vector,
                    vector
                )
            )

            results.append({
                "id_kb": kb.id_kb,
                "title": kb.title,
                "content": kb.content,
                "source_type": kb.source_type,
                "instagram_user_id":
                    kb.instagram_user_id,
                "similarity":
                    round(
                        float(score),
                        6
                    )
            })

        results.sort(
            key=lambda item:
                item["similarity"],
            reverse=True
        )

        return results[:top_k]

    @staticmethod
    def cosine_similarity(
        vector_a,
        vector_b
    ):

        # SentenceTransformer mengembalikan numpy.ndarray.
        # Jangan menggunakan `if not vector_a` karena dapat
        # memicu ValueError pada numpy array.
        if vector_a is None or vector_b is None:
            return 0.0

        if hasattr(vector_a, "tolist"):
            vector_a = vector_a.tolist()

        if hasattr(vector_b, "tolist"):
            vector_b = vector_b.tolist()

        if len(vector_a) == 0 or len(vector_b) == 0:
            return 0.0

        if len(vector_a) != len(vector_b):
            return 0.0

        numerator = sum(
            a * b
            for a, b
            in zip(
                vector_a,
                vector_b
            )
        )

        norm_a = (
            sum(
                a * a
                for a in vector_a
            )
            ** 0.5
        )

        norm_b = (
            sum(
                b * b
                for b in vector_b
            )
            ** 0.5
        )

        if (
            norm_a == 0
            or norm_b == 0
        ):
            return 0.0

        return (
            numerator
            /
            (
                norm_a *
                norm_b
            )
        )

    @staticmethod
    def update(
        id_kb,
        title,
        content,
        source_type="manual",
        instagram_user_id=None
    ):

        title = str(title or "").strip()
        content = str(content or "").strip()
        source_type = str(source_type or "manual").strip()

        if not title:
            raise ValueError(
                "Title knowledge base wajib diisi."
            )

        if not content:
            raise ValueError(
                "Content knowledge base wajib diisi."
            )

        active_user_id = (
            KnowledgeBaseService
            .get_active_instagram_user_id(
                instagram_user_id
            )
        )

        item = (
            Knowledge_Base.query
            .filter(
                Knowledge_Base.id_kb == id_kb,
                Knowledge_Base.instagram_user_id
                == active_user_id
            )
            .first()
        )

        if not item:
            return None

        try:

            item.title = title
            item.content = content
            item.source_type = (
                source_type or "manual"
            )

            # Isi dokumen berubah, maka embedding lama
            # harus dihapus agar vector tidak stale.
            Embeddings.query.filter_by(
                id_kb=id_kb
            ).delete(
                synchronize_session=False
            )

            db.session.flush()

            embedding = (
                KnowledgeBaseService
                .create_embedding(
                    item
                )
            )

            db.session.commit()

            return {
                "success": True,
                "knowledge_base": {
                    "id_kb":
                        item.id_kb,
                    "title":
                        item.title,
                    "content":
                        item.content,
                    "source_type":
                        item.source_type,
                    "instagram_user_id":
                        item.instagram_user_id,
                    "created_at":
                        item.created_at
                },
                "embedding": {
                    "id_embeddings":
                        embedding.id_embeddings,
                    "model_name":
                        embedding.model_name,
                    "dimension":
                        len(
                            json.loads(
                                embedding.vector_data
                            )
                        )
                }
            }

        except Exception:

            db.session.rollback()
            raise

    @staticmethod
    def delete(
        id_kb,
        instagram_user_id=None
    ):

        active_user_id = (
            KnowledgeBaseService
            .get_active_instagram_user_id(
                instagram_user_id
            )
        )

        item = (
            Knowledge_Base.query
            .filter(
                Knowledge_Base.id_kb == id_kb,
                Knowledge_Base.instagram_user_id
                == active_user_id
            )
            .first()
        )

        if not item:
            return False

        try:

            db.session.delete(
                item
            )

            db.session.commit()

            return True

        except Exception:

            db.session.rollback()
            raise
