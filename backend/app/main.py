from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import urllib.parse
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Thai Drill Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is missing")

# Parse Render Postgres URL
parsed = urllib.parse.urlparse(DATABASE_URL)
dbname = parsed.path[1:]
user = parsed.username
password = parsed.password
host = parsed.hostname
port = parsed.port or 5432

def get_db_connection():
    return psycopg2.connect(
        dbname=dbname, user=user, password=password,
        host=host, port=port, cursor_factory=RealDictCursor
    )

# Create table on startup
@app.on_event("startup")
async def startup():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            nickname TEXT PRIMARY KEY,
            starts INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

class StartRequest(BaseModel):
    nickname: str

@app.post("/api/quiz/start")
def start_quiz(req: StartRequest):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (nickname, starts)
        VALUES (%s, 1)
        ON CONFLICT (nickname)
        DO UPDATE SET starts = users.starts + 1
        RETURNING starts
    """, (req.nickname,))
    new_count = cur.fetchone()['starts']
    conn.commit()
    cur.close()
    conn.close()
    return {"nickname": req.nickname, "starts": new_count}

@app.get("/health")
def health():
    return {"status": "ok"}