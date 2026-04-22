# src/data/database.py
"""
In-memory mock database.
Swap these lists with real SQLAlchemy / Motor queries in production.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

# ── Models ────────────────────────────────────────────────────────────────────

@dataclass
class Movie:
    id: int
    title: str
    year: int
    genres: list[str]
    rating: float
    emoji: str
    description: str


@dataclass
class User:
    id: int
    name: str
    email: str
    avatar: str
    favorite_genres: list[str]
    watch_history: list[int]
    rating: dict[int, int]  # movie_id → score (1-5)


# ── Seed data ─────────────────────────────────────────────────────────────────

_MOVIES: list[Movie] = [
    Movie(1,  "Avengers: Endgame",        2019, ["Hành động", "Khoa học viễn tưởng"], 4.8, "⚡", "Siêu anh hùng Marvel tập hợp để chiến đấu chống lại Thanos."),
    Movie(2,  "Inception",                2010, ["Khoa học viễn tưởng", "Hành động"], 4.9, "🌀", "Một tên trộm chuyên xâm nhập vào giấc mơ để đánh cắp bí mật."),
    Movie(3,  "Interstellar",             2014, ["Khoa học viễn tưởng", "Tài liệu"],  4.7, "🌌", "Hành trình xuyên không gian để cứu nhân loại khỏi thảm họa."),
    Movie(4,  "Coco",                     2017, ["Hoạt hình", "Tình cảm"],            4.6, "💀", "Cậu bé Miguel phiêu lưu đến thế giới người chết để tìm tổ tiên."),
    Movie(5,  "The Dark Knight",          2008, ["Hành động", "Tội phạm"],            4.9, "🦇", "Batman đối đầu với Joker trong cuộc chiến sinh tử tại Gotham."),
    Movie(6,  "La La Land",               2016, ["Tình cảm", "Hài hước"],             4.5, "🎭", "Chuyện tình lãng mạn giữa một nhạc sĩ jazz và nữ diễn viên tại LA."),
    Movie(7,  "Get Out",                  2017, ["Kinh dị", "Tội phạm"],              4.4, "😱", "Chàng trai da đen phát hiện bí ẩn đáng sợ sau gia đình bạn gái."),
    Movie(8,  "Toy Story 4",              2019, ["Hoạt hình", "Phiêu lưu"],           4.3, "🪆", "Woody và các đồ chơi phiêu lưu trên hành trình mới đầy cảm xúc."),
    Movie(9,  "Dune",                     2021, ["Khoa học viễn tưởng", "Phiêu lưu"], 4.7, "🏜️", "Paul Atreides đến hành tinh Arrakis và khám phá số phận của mình."),
    Movie(10, "The Grand Budapest Hotel", 2014, ["Hài hước", "Tình cảm"],             4.5, "🏨", "Cuộc phiêu lưu hài hước của quản lý khách sạn danh tiếng Gustave H."),
    Movie(11, "Parasite",                 2019, ["Tội phạm", "Kinh dị"],              4.8, "🪲", "Gia đình nghèo xâm nhập vào cuộc sống xa hoa của gia đình giàu có."),
    Movie(12, "Joker",                    2019, ["Tội phạm", "Hành động"],            4.6, "🃏", "Hành trình bi thảm của Arthur Fleck trở thành tên tội phạm Joker."),
    Movie(13, "Apollo 13",                1995, ["Lịch sử", "Tài liệu"],              4.4, "🚀", "Cuộc khủng hoảng trên tàu vũ trụ Apollo 13 và nỗ lực cứu hộ."),
    Movie(14, "The Martian",              2015, ["Khoa học viễn tưởng", "Tài liệu"],  4.5, "👨‍🚀", "Phi hành gia Mark Watney sống sót một mình trên sao Hỏa."),
    Movie(15, "Spider-Man: No Way Home",  2021, ["Hoạt hình", "Hành động"],           4.7, "🕷️", "Spider-Man đối mặt với nhiều kẻ thù từ đa vũ trụ."),
    Movie(16, "Encanto",                  2021, ["Hoạt hình", "Tình cảm"],            4.4, "🌺", "Gia đình Madrigal với những phép màu đặc biệt ở vùng đất Colombia."),
]

_USERS: list[User] = [
    User(1, "Minh Tuấn", "tuan@cinema.vn", "👨‍💻",
         ["Hành động", "Khoa học viễn tưởng", "Kinh dị"],
         [1, 3, 5, 7, 9], {1: 5, 3: 4, 5: 5, 7: 3, 9: 4}),
    User(2, "Thu Hà", "ha@cinema.vn", "👩‍🎨",
         ["Tình cảm", "Hài hước", "Hoạt hình"],
         [2, 4, 6, 8, 10], {2: 5, 4: 4, 6: 5, 8: 4, 10: 3}),
    User(3, "Quang Huy", "huy@cinema.vn", "🧑‍🚀",
         ["Kinh dị", "Hành động", "Tội phạm"],
         [1, 2, 5, 11, 12], {1: 4, 2: 5, 5: 4, 11: 5, 12: 3}),
    User(4, "Bảo Linh", "linh@cinema.vn", "👩‍🔬",
         ["Tài liệu", "Lịch sử", "Khoa học viễn tưởng"],
         [3, 6, 9, 13, 14], {3: 5, 6: 4, 9: 5, 13: 4, 14: 5}),
    User(5, "Đức Anh", "anh@cinema.vn", "🧑‍🎤",
         ["Hoạt hình", "Hài hước", "Phiêu lưu"],
         [4, 8, 10, 15, 16], {4: 5, 8: 3, 10: 4, 15: 5, 16: 4}),
]


# ── Repositories ──────────────────────────────────────────────────────────────

class MovieRepository:
    @staticmethod
    def find_all() -> list[Movie]:
        return _MOVIES

    @staticmethod
    def find_by_id(movie_id: int) -> Optional[Movie]:
        return next((m for m in _MOVIES if m.id == movie_id), None)

    @staticmethod
    def find_by_genre(genre: str) -> list[Movie]:
        return sorted(
            [m for m in _MOVIES if any(g.lower() == genre.lower() for g in m.genres)],
            key=lambda m: m.rating, reverse=True,
        )

    @staticmethod
    def get_top_rated(limit: int = 10) -> list[Movie]:
        return sorted(_MOVIES, key=lambda m: m.rating, reverse=True)[:limit]

    @staticmethod
    def get_all_genres() -> list[str]:
        genres: set[str] = set()
        for m in _MOVIES:
            genres.update(m.genres)
        return sorted(genres)

    @staticmethod
    def get_stats() -> dict:
        total_ratings = sum(len(u.rating) for u in _USERS)
        return {
            "total_movies": len(_MOVIES),
            "total_users": len(_USERS),
            "total_genres": len(MovieRepository.get_all_genres()),
            "total_ratings": total_ratings,
        }


class UserRepository:
    @staticmethod
    def find_all() -> list[User]:
        return _USERS

    @staticmethod
    def find_by_id(user_id: int) -> Optional[User]:
        return next((u for u in _USERS if u.id == user_id), None)

    @staticmethod
    def get_unwatched_movies(user_id: int) -> list[Movie]:
        user = UserRepository.find_by_id(user_id)
        if not user:
            return []
        return sorted(
            [m for m in _MOVIES if m.id not in user.watch_history],
            key=lambda m: m.rating, reverse=True,
        )

    @staticmethod
    def get_recommended_movies(user_id: int, limit: int = 6) -> list[Movie]:
        user = UserRepository.find_by_id(user_id)
        if not user:
            return []
        unwatched = UserRepository.get_unwatched_movies(user_id)
        by_genre = [m for m in unwatched if any(g in user.favorite_genres for g in m.genres)]
        extras   = [m for m in unwatched if m not in by_genre]
        return (by_genre + extras)[:limit]
