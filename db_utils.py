import json
import sqlite3
from pathlib import Path

DB_NAME = "car_dealership.db"


def load_json(file: str):
    """Загружает данные из JSON-файла."""
    path = Path(file)
    if not path.exists():
        raise FileNotFoundError(f"Файл {file} не найден")
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def get_connection() -> sqlite3.Connection:
    """Соединение с SQLite. row_factory — чтобы читать колонки по имени."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
