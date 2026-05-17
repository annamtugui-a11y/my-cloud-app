from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect("/data/users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Baza de date gata!")

@app.on_event("startup")
def startup():
    init_db()

class User(BaseModel):
    name: str

@app.post("/users")
def create_user(user: User):
    conn = get_db()
    cur = conn.execute("INSERT INTO users (name) VALUES (?)", (user.name,))
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return {"id": user_id, "name": user.name}

@app.get("/users")
def get_users():
    conn = get_db()
    rows = conn.execute("SELECT id, name, created_at FROM users").fetchall()
    conn.close()
    return [{"id": r["id"], "name": r["name"], "created_at": r["created_at"]} for r in rows]
