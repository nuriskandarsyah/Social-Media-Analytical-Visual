from flask import Blueprint, request, jsonify

from services.knowledge_base_service import (
    KnowledgeBaseService
)


knowledge_base_bp = Blueprint(
    "knowledge_base",
    __name__,
    url_prefix="/api/knowledge-base"
)


def get_instagram_user_id():

    value = request.args.get(
        "instagram_user_id"
    )

    if value:
        return str(value).strip()

    payload = (
        request.get_json(
            silent=True
        )
        or {}
    )

    value = payload.get(
        "instagram_user_id"
    )

    if value:
        return str(value).strip()

    return None


@knowledge_base_bp.route(
    "/",
    methods=["GET"]
)
def get_documents():

    try:

        data = (
            KnowledgeBaseService
            .get_all(
                get_instagram_user_id()
            )
        )

        return jsonify({
            "success": True,
            "message":
                "Data Knowledge Base berhasil diambil",
            "data": data
        }), 200

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "success": False,
            "message":
                "Gagal mengambil data Knowledge Base",
            "error": str(e)
        }), 500


@knowledge_base_bp.route(
    "/create",
    methods=["POST"]
)
def create_document():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    title = data.get(
        "title"
    )

    content = data.get(
        "content"
    )

    source_type = data.get(
        "source_type",
        "manual"
    )

    instagram_user_id = data.get(
        "instagram_user_id"
    )

    if not title:

        return jsonify({
            "success": False,
            "message":
                "Title wajib diisi"
        }), 400

    if not content:

        return jsonify({
            "success": False,
            "message":
                "Content wajib diisi"
        }), 400

    try:

        result = (
            KnowledgeBaseService
            .create_with_embedding(
                title=title,
                content=content,
                source_type=source_type,
                instagram_user_id=
                    instagram_user_id
            )
        )

        return jsonify({
            "success": True,
            "message":
                "Knowledge Base dan embedding berhasil dibuat",
            "data": result
        }), 201

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "success": False,
            "message":
                "Gagal membuat Knowledge Base",
            "error": str(e)
        }), 500


@knowledge_base_bp.route(
    "/<int:id_kb>",
    methods=["GET"]
)
def get_document(id_kb):

    try:

        instagram_user_id = (
            get_instagram_user_id()
        )

        data = (
            KnowledgeBaseService
            .get_by_id(
                id_kb,
                instagram_user_id
            )
        )

        if not data:

            return jsonify({
                "success": False,
                "message":
                    "Knowledge Base tidak ditemukan"
            }), 404

        data["embedding"] = (
            KnowledgeBaseService
            .get_embedding(
                id_kb,
                instagram_user_id
            )
        )

        return jsonify({
            "success": True,
            "message":
                "Detail Knowledge Base berhasil diambil",
            "data": data
        }), 200

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "success": False,
            "message":
                "Gagal mengambil detail Knowledge Base",
            "error": str(e)
        }), 500


@knowledge_base_bp.route(
    "/search",
    methods=["POST"]
)
def search_document():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    query = data.get(
        "query"
    )

    top_k = data.get(
        "top_k",
        5
    )

    instagram_user_id = data.get(
        "instagram_user_id"
    )

    if not query:

        return jsonify({
            "success": False,
            "message":
                "Query wajib diisi"
        }), 400

    try:

        results = (
            KnowledgeBaseService
            .search(
                query=query,
                top_k=top_k,
                instagram_user_id=
                    instagram_user_id
            )
        )

        return jsonify({
            "success": True,
            "message":
                "Pencarian Knowledge Base berhasil",
            "data": results
        }), 200

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "success": False,
            "message":
                "Pencarian Knowledge Base gagal",
            "error": str(e)
        }), 500


@knowledge_base_bp.route(
    "/<int:id_kb>",
    methods=["PUT"]
)
def update_document(id_kb):

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    title = data.get(
        "title"
    )

    content = data.get(
        "content"
    )

    source_type = data.get(
        "source_type",
        "manual"
    )

    instagram_user_id = data.get(
        "instagram_user_id"
    )

    if not title:

        return jsonify({
            "success": False,
            "message":
                "Title wajib diisi"
        }), 400

    if not content:

        return jsonify({
            "success": False,
            "message":
                "Content wajib diisi"
        }), 400

    try:

        result = (
            KnowledgeBaseService
            .update(
                id_kb=id_kb,
                title=title,
                content=content,
                source_type=source_type,
                instagram_user_id=
                    instagram_user_id
            )
        )

        if not result:

            return jsonify({
                "success": False,
                "message":
                    "Knowledge Base tidak ditemukan"
            }), 404

        return jsonify({
            "success": True,
            "message":
                "Knowledge Base berhasil diperbarui",
            "data": result
        }), 200

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "success": False,
            "message":
                "Gagal memperbarui Knowledge Base",
            "error": str(e)
        }), 500


@knowledge_base_bp.route(
    "/<int:id_kb>",
    methods=["DELETE"]
)
def delete_document(id_kb):

    try:

        instagram_user_id = (
            get_instagram_user_id()
        )

        deleted = (
            KnowledgeBaseService
            .delete(
                id_kb,
                instagram_user_id
            )
        )

        if not deleted:

            return jsonify({
                "success": False,
                "message":
                    "Knowledge Base tidak ditemukan"
            }), 404

        return jsonify({
            "success": True,
            "message":
                "Knowledge Base berhasil dihapus"
        }), 200

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "success": False,
            "message":
                "Gagal menghapus Knowledge Base",
            "error": str(e)
        }), 500
