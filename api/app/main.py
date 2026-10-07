"""Cloud Notes API: PostgreSQL persisten dan Redis untuk cache daftar."""

import json
import os
from pathlib import Path

import psycopg
from fastapi import FastAPI, HTTPException, Response, status
from psycopg.rows import dict_row
from pydantic import BaseModel, Field, field_validator
from redis import Redis
from redis.exceptions import RedisError

app = FastAPI(title="Cloud Notes", version="0.6")
cache = Redis.from_url(
    os.getenv("REDIS_URL", "redis://cache:6379/0"),
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)


class NoteInput(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=5000)

    @field_validator("title", "content")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        """Jangan simpan catatan yang tampak kosong setelah whitespace dipangkas."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("teks tidak boleh hanya berisi spasi")
        return cleaned


def db_connection():
    password_file = Path(os.getenv("DB_PASSWORD_FILE", "/run/secrets/db_password"))
    password = password_file.read_text(encoding="utf-8").strip()
    return psycopg.connect(
        host=os.getenv("DB_HOST", "db"),
        dbname=os.getenv("DB_NAME", "cloudnotes"),
        user=os.getenv("DB_USER", "clouduser"),
        password=password,
        connect_timeout=3,
        row_factory=dict_row,
    )


def clear_list_cache() -> None:
    try:
        cache.delete("notes:list")
    except RedisError:
        pass  # Database tetap sumber kebenaran ketika cache gagal.


@app.get("/health")
def health() -> dict:
    try:
        with db_connection() as conn:
            conn.execute("SELECT 1")
        cache.ping()
    except (OSError, psycopg.Error, RedisError) as exc:
        raise HTTPException(status_code=503, detail="Dependency tidak sehat") from exc
    return {"status": "ok", "database": "postgres", "cache": "redis"}


@app.get("/notes")
def list_notes(response: Response) -> list[dict]:
    cache_available = True
    try:
        saved = cache.get("notes:list")
        if saved is not None:
            response.headers["X-Cache"] = "HIT"
            return json.loads(saved)
    except json.JSONDecodeError:
        # Data cache dapat rusak; buang salinannya dan baca sumber kebenaran.
        try:
            cache.delete("notes:list")
        except RedisError:
            cache_available = False
    except RedisError:
        cache_available = False
    with db_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, content, created_at FROM notes ORDER BY id DESC"
        ).fetchall()
    result = [{**row, "created_at": row["created_at"].isoformat()} for row in rows]
    if cache_available:
        try:
            cache.setex("notes:list", 30, json.dumps(result))
        except RedisError:
            pass
    response.headers["X-Cache"] = "MISS"
    return result


@app.post("/notes", status_code=status.HTTP_201_CREATED)
def create_note(note: NoteInput) -> dict:
    with db_connection() as conn:
        row = conn.execute(
            "INSERT INTO notes (title, content) VALUES (%s, %s) "
            "RETURNING id, title, content, created_at",
            (note.title, note.content),
        ).fetchone()
    clear_list_cache()
    return {**row, "created_at": row["created_at"].isoformat()}


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int) -> Response:
    with db_connection() as conn:
        row = conn.execute("DELETE FROM notes WHERE id = %s RETURNING id", (note_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Note tidak ditemukan")
    clear_list_cache()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
