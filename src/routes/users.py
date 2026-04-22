# src/routes/users.py
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from src.data.database import UserRepository, MovieRepository

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/")
async def list_users():
    users = [
        {"id": u.id, "name": u.name, "email": u.email,
         "avatar": u.avatar, "favorite_genres": u.favorite_genres,
         "watch_history_count": len(u.watch_history)}
        for u in UserRepository.find_all()
    ]
    return {"success": True, "data": users}


@router.get("/{user_id}")
async def get_user(user_id: int):
    user = UserRepository.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return {"success": True, "data": user}


@router.get("/{user_id}/recommendations")
async def get_recommendations(user_id: int, limit: int = Query(default=6, ge=1, le=20)):
    user = UserRepository.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    movies = UserRepository.get_recommended_movies(user_id, limit)
    return {"success": True, "user_id": user_id, "user_name": user.name, "data": movies}


@router.get("/{user_id}/history")
async def get_watch_history(user_id: int):
    user = UserRepository.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    history = []
    for mid in user.watch_history:
        movie = MovieRepository.find_by_id(mid)
        if movie:
            history.append({**movie.__dict__, "user_rating": user.rating.get(mid)})
    return {"success": True, "data": history}
