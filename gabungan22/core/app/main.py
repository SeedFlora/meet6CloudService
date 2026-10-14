"""API Cloud Notes yang masih menyimpan data di memori container."""

import os
from threading import Lock

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Cloud Notes", version="0.5")
_notes: dict[int, dict] = {}
_next_id = 1
_lock = Lock()


class NoteInput(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=5000)

    @field_validator("title", "content")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        """Simpan teks yang rapi; spasi saja bukan catatan yang valid."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("teks tidak boleh hanya berisi spasi")
        return cleaned


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "cloud-notes-api"}


@app.get("/runtime")
def runtime() -> dict:
    return {"environment": os.getenv("APP_ENV", "local"), "storage": "memory"}


@app.get("/notes")
def list_notes() -> list[dict]:
    with _lock:
        return list(_notes.values())


@app.post("/notes", status_code=status.HTTP_201_CREATED)
def create_note(note: NoteInput) -> dict:
    global _next_id
    with _lock:
        item = {"id": _next_id, **note.model_dump()}
        _notes[_next_id] = item
        _next_id += 1
        return item


@app.get("/notes/{note_id}")
def get_note(note_id: int) -> dict:
    with _lock:
        item = _notes.get(note_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Note tidak ditemukan")
    return item
