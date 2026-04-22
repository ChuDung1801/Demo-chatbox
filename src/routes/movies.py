# src/routes/movies.py
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from src.data.database import MovieRepository

router = APIRouter(prefix="/api/movies", tags=["movies"])


@router.get("/genres")
async def list_genres():
    return {"success": True, "data": MovieRepository.get_all_genres()}


@router.get("/stats")
async def get_stats():
    return {"success": True, "data": MovieRepository.get_stats()}


@router.get("/")
async def list_movies(
    genre:     str | None = Query(default=None),
    top_rated: bool       = Query(default=False, alias="topRated"),
    limit:     int        = Query(default=16, ge=1, le=50),
):
    if genre:
        movies = MovieRepository.find_by_genre(genre)
    elif top_rated:
        movies = MovieRepository.get_top_rated(limit)
    else:
        movies = MovieRepository.find_all()
    return {"success": True, "total": len(movies), "data": movies}


@router.get("/{movie_id}")
async def get_movie(movie_id: int):
    movie = MovieRepository.find_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Không tìm thấy phim")
    return {"success": True, "data": movie}
