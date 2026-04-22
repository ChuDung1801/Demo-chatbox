# src/langchain_chain/chain.py
"""
CineBot LangChain Pipeline — langchain-core==1.3.0
====================================================
Flow:
    user message
        │
        ▼
    build_database_context(user_id)          ← injects live DB snapshot
        │
        ▼
    ChatPromptTemplate (system + history + human)
        │
        ▼
    ChatAnthropic (claude-sonnet-4-20250514)
        │
        ▼
    MovieOutputParser (extracts text + movieIds from <MOVIES> tag)
        │
        ▼
    { text: str, movie_ids: list[int] }
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional

# ── LangChain core 1.3.0 ──────────────────────────────────────────────────────
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# ── LangChain Anthropic partner ───────────────────────────────────────────────
from langchain_groq import ChatGroq

# ── Memory (langchain 0.3.x) ─────────────────────────────────────────────────
from langchain_core.chat_history import InMemoryChatMessageHistory
# ── Local DB ──────────────────────────────────────────────────────────────────
from src.data.database import UserRepository, MovieRepository

logger = logging.getLogger(__name__)

# ── 1. LLM ────────────────────────────────────────────────────────────────────

def _build_llm() -> ChatGroq:
    """Instantiate ChatGroq — reads GROQ_API_KEY from env automatically."""
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        max_tokens=1024,
        temperature=0.7,
    )


# ── 2. System Prompt Template ─────────────────────────────────────────────────

_SYSTEM_TEMPLATE = """\
Bạn là **CineBot** — trợ lý AI gợi ý phim thông minh cho hệ thống rạp chiếu phim.
Bạn có quyền truy cập đầy đủ vào cơ sở dữ liệu phim và người dùng.
Luôn trả lời **bằng tiếng Việt**, thân thiện và hữu ích.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{user_block}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## CƠ SỞ DỮ LIỆU PHIM ({total_movies} phim)
{movie_block}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## NGƯỜI DÙNG HỆ THỐNG ({total_users} người)
{users_block}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## QUY TẮC GỢI Ý
1. Ưu tiên thể loại yêu thích của người dùng hiện tại.
2. Loại trừ những phim người dùng đã xem.
3. Sắp xếp theo điểm rating từ cao đến thấp.
4. Giải thích ngắn gọn lý do gợi ý (1-2 câu mỗi phim).
5. Tối đa 6 phim mỗi lần gợi ý.
6. Khi liệt kê phim, LUÔN kèm tag JSON đặc biệt để frontend render card:
   <MOVIES>[{{"id":1}},{{"id":3}},{{"id":5}}]</MOVIES>
7. Nếu chưa có người dùng, nhắc họ chọn tài khoản.
"""


def _build_database_context(user_id: Optional[int]) -> dict[str, str]:
    """Snapshot toàn bộ DB + user profile vào các biến cho prompt template."""

    # --- user block ---
    user = UserRepository.find_by_id(user_id) if user_id else None
    if user:
        watched_titles = ", ".join(
            m.title for mid in user.watch_history
            if (m := MovieRepository.find_by_id(mid))
        )
        highly_rated = ", ".join(
            MovieRepository.find_by_id(int(mid)).title
            for mid, score in user.rating.items()
            if score >= 4 and MovieRepository.find_by_id(int(mid))
        ) or "chưa có"
        user_block = (
            f"## NGƯỜI DÙNG HIỆN TẠI\n"
            f"ID       : {user.id}\n"
            f"Tên      : {user.name} {user.avatar}\n"
            f"Email    : {user.email}\n"
            f"Yêu thích: {', '.join(user.favorite_genres)}\n"
            f"Đã xem   : {watched_titles}\n"
            f"Đánh giá cao (≥4⭐): {highly_rated}"
        )
    else:
        user_block = "## CHƯA CHỌN NGƯỜI DÙNG\nYêu cầu người dùng chọn tài khoản trước khi tiếp tục."

    # --- movie catalog ---
    movie_lines = []
    for m in MovieRepository.find_all():
        movie_lines.append(
            f"[ID:{m.id}] {m.emoji} {m.title} ({m.year}) | "
            f"Thể loại: {'/'.join(m.genres)} | Rating: {m.rating}/5\n"
            f"  Mô tả: {m.description}"
        )
    movie_block = "\n".join(movie_lines)

    # --- users summary ---
    users_lines = [
        f"[ID:{u.id}] {u.avatar} {u.name} | "
        f"Yêu thích: {', '.join(u.favorite_genres)} | "
        f"Đã xem: {len(u.watch_history)} phim"
        for u in UserRepository.find_all()
    ]
    users_block = "\n".join(users_lines)

    stats = MovieRepository.get_stats()
    return {
        "user_block": user_block,
        "movie_block": movie_block,
        "users_block": users_block,
        "total_movies": str(stats["total_movies"]),
        "total_users": str(stats["total_users"]),
    }


# ── 3. Prompt Template ────────────────────────────────────────────────────────

def _build_prompt() -> ChatPromptTemplate:
    """
    LangChain 1.3.0 ChatPromptTemplate with:
      - system message (dynamic DB context injected at invoke time)
      - MessagesPlaceholder for conversation history
      - human message
    """
    return ChatPromptTemplate.from_messages([
        ("system", _SYSTEM_TEMPLATE),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])


# ── 4. Output Parser ──────────────────────────────────────────────────────────

_MOVIES_TAG_RE = re.compile(r"<MOVIES>(.*?)</MOVIES>", re.DOTALL)


class MovieOutputParser(StrOutputParser):
    """
    Extends StrOutputParser to also extract structured movie IDs
    from the <MOVIES>[{"id":1}, ...]</MOVIES> tag emitted by the LLM.
    """

    def parse_structured(self, text: str) -> dict:
        """
        Returns:
            {
                "text":      cleaned response text (tag removed),
                "movie_ids": list of integer movie IDs
            }
        """
        movie_ids: list[int] = []
        match = _MOVIES_TAG_RE.search(text)

        if match:
            try:
                items = json.loads(match.group(1))
                movie_ids = [int(item["id"]) for item in items if "id" in item]
            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                logger.warning("MovieOutputParser: failed to parse MOVIES tag — %s", exc)

        clean_text = _MOVIES_TAG_RE.sub("", text).strip()
        return {"text": clean_text, "movie_ids": movie_ids}


# ── 5. Session Memory Store ───────────────────────────────────────────────────

# { session_id → InMemoryChatMessageHistory }
_session_store: dict[str, InMemoryChatMessageHistory] = {}


def _get_or_create_memory(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _session_store:
        _session_store[session_id] = InMemoryChatMessageHistory(
            return_messages=True,
            memory_key="history",
            input_key="input",
            output_key="output",
        )
    return _session_store[session_id]


def clear_session(session_id: str) -> None:
    """Remove conversation memory for a given session."""
    _session_store.pop(session_id, None)


# ── 6. RunnableSequence (chain) ───────────────────────────────────────────────

def _build_chain() -> RunnableSequence:
    """
    Stateless chain — memory is loaded externally and passed as `history`.
    Pipeline: ChatPromptTemplate → ChatAnthropic → StrOutputParser
    """
    return _build_prompt() | _build_llm() | StrOutputParser()


# ── 7. Public entry point ─────────────────────────────────────────────────────

_output_parser = MovieOutputParser()


async def chat(
    session_id: str,
    message: str,
    user_id: Optional[int] = None,
) -> dict:
    """
    Main async entry point called by the FastAPI route.

    Args:
        session_id: Unique session key (e.g. "user_1_xyz")
        message:    Raw user message
        user_id:    Active user ID, or None for anonymous

    Returns:
        { "text": str, "movie_ids": list[int] }
    """
    chain  = _build_chain()
    memory = _get_or_create_memory(session_id)
    ctx    = _build_database_context(user_id)

    # Load conversation history from memory
    # mem_vars: dict = memory.load_memory_variables({})
    # history: list[BaseMessage] = mem_vars.get("history", [])
    history: list[BaseMessage] = memory.messages

    # Invoke the chain
    raw_output: str = await chain.ainvoke({
        **ctx,
        "history": history,
        "input": message,
    })

    # Persist this turn
    # memory.save_context({"input": message}, {"output": raw_output})
    memory.add_user_message(message)
    memory.add_ai_message(raw_output)

    # Parse structured output
    return _output_parser.parse_structured(raw_output)
