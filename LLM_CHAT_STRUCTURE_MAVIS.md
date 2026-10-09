# Struktur LLM Chat MAVis

## File yang sudah ada

### Controller
`controllers/llm_chat_controller.py`

Endpoint yang tersedia:

`POST /api/llm-chat/`

Controller menerima JSON:

```json
{"message": "pertanyaan pengguna"}
```

Lalu memanggil:

```python
LLMChatService.chat(message=message)
```

dan mengembalikan `success`, `message`, dan `data`. Struktur ini terlihat langsung pada controller yang kamu kirim. fileciteturn180file0L1-L16

### Service
`services/llm_chat_service.py`

Service yang tersedia saat ini memiliki alur:

```text
chat()
  ↓
get_context()
  ↓
KnowledgeBaseService.search()
  ↓
build_prompt()
  ↓
generate()
  ↓
Gemini
```

`get_context()` menggunakan `KnowledgeBaseService.search()` dan mengambil top-K context; `build_prompt()` meminta model menjawab berdasarkan Knowledge Base dan tidak mengarang data. fileciteturn180file1L29-L103

Generation saat ini memakai client Gemini dan mengembalikan `interaction.output_text`. fileciteturn180file1L106-L135

## Struktur project

```text
mavis/
├── controllers/
│   └── llm_chat_controller.py
│
├── services/
│   ├── llm_chat_service.py
│   └── knowledge_base_service.py
│
├── models/
│   └── ...
│
└── app.py
```

Frontend yang nantinya cocok:

```text
frontend/src/
├── pages/
│   └── LLMChat.jsx
├── components/
│   └── llm/
│       ├── ChatMessage.jsx
│       ├── ChatInput.jsx
│       └── SourceList.jsx
└── services/
    └── llmChatApi.js
```

## Kontrak API

Request:

```json
{
  "message": "Apa fungsi K-Means++ pada MAVis?"
}
```

Response sukses mengikuti struktur service saat ini:

```json
{
  "success": true,
  "message": "LLM Chat berhasil",
  "data": {
    "question": "...",
    "answer": "...",
    "sources": [],
    "model": "..."
  }
}
```

Service memang mengembalikan `question`, `answer`, `sources`, dan nama model. fileciteturn180file1L136-L168

## Prinsip

```text
Controller
    = HTTP/API

LLMChatService
    = retrieval + prompt + generation

KnowledgeBaseService
    = pencarian knowledge base

Gemini
    = menghasilkan jawaban

Frontend
    = UI percakapan
```

Jangan memindahkan query Knowledge Base atau pemanggilan Gemini langsung ke controller.

## Status saat ini

Controller dan service sudah merupakan fondasi LLM Chat. Yang belum ditentukan dari dua file ini adalah:
- registrasi blueprint di `app.py`,
- UI `LLMChat.jsx`,
- `llmChatApi.js`,
- dan mekanisme memory percakapan multi-turn bila nanti dibutuhkan.

Dokumen ini sengaja tidak menambahkan asumsi di luar dua file yang kamu kirim.
