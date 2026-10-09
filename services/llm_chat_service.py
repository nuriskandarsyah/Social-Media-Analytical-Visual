import os

from google import genai

from services.knowledge_base_service import KnowledgeBaseService


class LLMChatService:

    MODEL_NAME = "gemini-3.6-flash"

    # =========================================================
    # GEMINI CLIENT
    # =========================================================

    @staticmethod
    def get_client():
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY belum dikonfigurasi."
            )

        return genai.Client(
            api_key=api_key
        )

    # =========================================================
    # KNOWLEDGE BASE CONTEXT
    # =========================================================

    @staticmethod
    def get_context(
        message,
        instagram_user_id=None,
        top_k=3
    ):
        results = KnowledgeBaseService.search(
            query=message,
            top_k=top_k,
            instagram_user_id=instagram_user_id
        )

        if not results:
            return {
                "context": "",
                "sources": []
            }

        context_parts = []
        sources = []

        for index, item in enumerate(results, start=1):

            title = (
                item.get("title")
                or f"Dokumen {index}"
            )

            content = (
                item.get("content")
                or ""
            )

            similarity = item.get(
                "similarity"
            )

            context_parts.append(
                f"""
SUMBER {index}
Judul: {title}
Isi:
{content}
""".strip()
            )

            sources.append({
                "id_kb": item.get("id_kb"),
                "title": title,
                "similarity": similarity
            })

        return {
            "context": "\n\n".join(
                context_parts
            ),
            "sources": sources
        }

    # =========================================================
    # PROMPT
    # =========================================================

    @staticmethod
    def build_prompt(
        message,
        context
    ):
        if context.strip():
            knowledge_section = context
        else:
            knowledge_section = (
                "Tidak ada dokumen Knowledge Base "
                "yang relevan ditemukan."
            )

        return f"""
Kamu adalah MAVisupport, asisten AI pada sistem MAVis
(Meta Analytical Visual).

Tugas kamu adalah membantu pengguna menjawab pertanyaan
berdasarkan Knowledge Base perusahaan.

ATURAN:
1. Gunakan informasi dari Knowledge Base sebagai sumber utama.
2. Jangan mengarang informasi perusahaan.
3. Jika jawaban tidak tersedia di Knowledge Base,
   katakan dengan jujur bahwa informasi tersebut belum tersedia.
4. Jawab dalam bahasa Indonesia.
5. Jawab dengan jelas, singkat, dan mudah dipahami.
6. Jangan menyebut proses internal RAG, embedding,
   atau sistem retrieval kepada pengguna kecuali ditanyakan.

KNOWLEDGE BASE:
{knowledge_section}

PERTANYAAN PENGGUNA:
{message}

JAWAB:
""".strip()

    # =========================================================
    # GENERATE
    # =========================================================

    @staticmethod
    def generate(
        prompt
    ):
        client = LLMChatService.get_client()

        response = client.interactions.create(
            model=LLMChatService.MODEL_NAME,
            input=prompt
        )

        answer = getattr(
            response,
            "output_text",
            None
        )

        if not answer:
            raise ValueError(
                "Gemini tidak mengembalikan jawaban."
            )

        return answer.strip()

    # =========================================================
    # CHAT
    # =========================================================

    @staticmethod
    def chat(
        message,
        instagram_user_id=None
    ):
        context_data = LLMChatService.get_context(
            message=message,
            instagram_user_id=instagram_user_id,
            top_k=3
        )

        prompt = LLMChatService.build_prompt(
            message=message,
            context=context_data["context"]
        )

        answer = LLMChatService.generate(
            prompt=prompt
        )

        return {
            "question": message,
            "answer": answer,
            "sources": context_data["sources"],
            "model": LLMChatService.MODEL_NAME
        }