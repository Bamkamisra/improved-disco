from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi.middleware.cors import CORSMiddleware

# Database Setup (Replace with your actual Postgres credentials)
# Format: postgresql://username:password@host:port/database_name
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost/thai_quiz_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True, index=True)
    streak_counter = Column(Integer, default=0)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow CORS so the frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Model
class StartQuizRequest(BaseModel):
    nickname: str

@app.post("/start")
def start_quiz(request: StartQuizRequest):
    db = SessionLocal()
    
    # Check if user exists
    user = db.query(User).filter(User.nickname == request.nickname).first()
    
    if not user:
        # Create new user with a streak of 1
        user = User(nickname=request.nickname, streak_counter=1)
        db.add(user)
    else:
        # Increment existing user's streak
        user.streak_counter += 1
        
    db.commit()
    db.refresh(user)
    
    streak = user.streak_counter
    db.close()
    
    return {
        "message": "Quiz started", 
        "nickname": user.nickname, 
        "streak_counter": streak
    }