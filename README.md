# 🎬 CineBot Backend — Python

**FastAPI + LangChain `langchain-core==1.3.0` + Anthropic Claude**

---

## Kiến trúc

```
HTTP Request  POST /api/chat  { session_id, user_id, message }
      │
      ▼
 FastAPI  (src/app.py)
  ├── POST /api/chat          → src/routes/chat.py
  ├── GET  /api/users/...     → src/routes/users.py
  └── GET  /api/movies/...    → src/routes/movies.py
      │
      ▼
 LangChain Pipeline  (src/langchain_chain/chain.py)
  │
  ├── build_database_context(user_id)
  │     └── UserRepository + MovieRepository → context strings
  │
  ├── ChatPromptTemplate.from_messages([
  │       ("system",  _SYSTEM_TEMPLATE),        ← DB snapshot injected here
  │       MessagesPlaceholder("history"),        ← ConversationBufferMemory
  │       ("human",   "{input}"),
  │   ])
  │
  ├── ChatAnthropic(model="claude-sonnet-4-20250514")
  │
  └── MovieOutputParser.parse_structured(raw)
        → { "text": str, "movie_ids": [1, 3, 5] }
      │
      ▼
 src/data/database.py
  ├── UserRepository
  └── MovieRepository
```

---

## Cài đặt (clone từ GitHub)

### Bước 1 — Clone repo LangChain về local

```bash
git clone https://github.com/langchain-ai/langchain.git
cd langchain

# Checkout đúng tag stable mới nhất
git checkout tags/langchain-core==1.3.0
```

### Bước 2 — Cài các package LangChain từ source local

```bash
# Tạo virtualenv cho project CineBot
cd /đường/dẫn/tới/cinebot-py
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Cài langchain-core 1.3.0 từ source đã clone
pip install /đường/dẫn/tới/langchain/libs/core

# Cài langchain chính từ source
pip install /đường/dẫn/tới/langchain/libs/langchain

# Cài partner Anthropic từ source
pip install /đường/dẫn/tới/langchain/libs/partners/anthropic
```

### Bước 3 — Cài các dependency còn lại

```bash
# Từ thư mục cinebot-py
pip install fastapi uvicorn[standard] pydantic python-dotenv httpx
```

> **Hoặc nếu chỉ dùng PyPI** (không cần clone):
> ```bash
> pip install -r requirements.txt
> ```

### Bước 4 — Cấu hình môi trường

```bash
cp .env.example .env
# Mở .env, điền ANTHROPIC_API_KEY
```

### Bước 5 — Chạy server

```bash
python main.py
# hoặc
uvicorn main:app --reload --port 8000
```

Server chạy tại: `http://localhost:8000`
Swagger UI:      `http://localhost:8000/docs`

---

## Cấu trúc thư mục

```
cinebot-py/
├── main.py                        # Entry point
├── requirements.txt
├── .env.example
└── src/
    ├── app.py                     # FastAPI app factory + middleware
    ├── data/
    │   └── database.py            # Mock DB + UserRepository + MovieRepository
    ├── langchain_chain/
    │   └── chain.py               # ⭐ LangChain 1.3.0 pipeline
    └── routes/
        ├── chat.py                # POST /api/chat
        ├── users.py               # GET  /api/users
        └── movies.py              # GET  /api/movies
```

---

## API Reference

### Chat

| Method | Endpoint | Body |
|--------|----------|------|
| `POST` | `/api/chat/` | `{ session_id, message, user_id? }` |
| `DELETE` | `/api/chat/session/{session_id}` | — |

**Request:**
```json
{
  "session_id": "user_1_abc",
  "user_id": 1,
  "message": "Gợi ý phim phù hợp với tôi"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "user_1_abc",
  "reply": "Dựa trên sở thích của bạn...",
  "movie_ids": [2, 9, 12]
}
```

### Users

| Endpoint | Mô tả |
|----------|-------|
| `GET /api/users/` | Danh sách tất cả users |
| `GET /api/users/{id}` | Chi tiết 1 user |
| `GET /api/users/{id}/recommendations` | Phim gợi ý cho user |
| `GET /api/users/{id}/history` | Lịch sử xem phim |

### Movies

| Endpoint | Query | Mô tả |
|----------|-------|-------|
| `GET /api/movies/` | `?genre=&topRated=true&limit=` | Danh sách phim |
| `GET /api/movies/genres` | — | Tất cả thể loại |
| `GET /api/movies/stats` | — | Thống kê hệ thống |
| `GET /api/movies/{id}` | — | Chi tiết 1 phim |

---

## Kết nối Frontend

Trong `movie-chatbox.html`, thay hàm `callClaude()`:

```js
async function callClaude(userMessage) {
  const res = await fetch("http://localhost:8000/api/chat/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: `user_${currentUser?.id ?? "anon"}_session`,
      user_id:    currentUser?.id ?? null,
      message:    userMessage,
    }),
  });
  const data = await res.json();
  return { text: data.reply, movieIds: data.movie_ids };
}
```

---

## LangChain 1.3.0 Components

| Component | Class | Vai trò |
|---|---|---|
| **LLM** | `ChatAnthropic` | Gọi Claude Sonnet |
| **Prompt** | `ChatPromptTemplate.from_messages()` | System + History + Human |
| **Placeholder** | `MessagesPlaceholder("history")` | Inject lịch sử hội thoại |
| **Memory** | `ConversationBufferMemory` | Lưu theo session in-memory |
| **Parser** | `MovieOutputParser(StrOutputParser)` | Tách `<MOVIES>` tag → `movie_ids` |
| **Chain** | `prompt \| llm \| parser` (pipe syntax) | LCEL RunnableSequence |
