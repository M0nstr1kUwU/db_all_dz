import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import secrets
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Используем DATABASE_URL из переменных окружения
DATABASE_URL = os.getenv('DATABASE_URL')

# Если DATABASE_URL не установлен, используем локальную базу (только для разработки)
if not DATABASE_URL:
    DATABASE_URL = 'postgresql://postgres:password@localhost:5432/code_snippets'

if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)


STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def connect_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")

        # Проверяем, что таблицы созданы
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"Available tables: {', '.join(tables)}")

    except Exception as e:
        print(f"Error creating tables: {e}")


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(256), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    first_name = Column(String(256))
    last_name = Column(String(256))
    nick_name = Column(String(256))
    created_at = Column(String(256), default=lambda: datetime.utcnow().isoformat())

    snippets = relationship("Snippet", back_populates="author")
    likes = relationship("Like", back_populates="user")


class Snippet(Base):
    __tablename__ = 'snippets'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(256), nullable=False)
    code = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(String(256), default=lambda: datetime.utcnow().isoformat())

    author = relationship("User", back_populates="snippets")
    likes = relationship("Like", back_populates="snippet")


class Like(Base):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    snippet_id = Column(Integer, ForeignKey('snippets.id'))
    created_at = Column(String(256), default=lambda: datetime.utcnow().isoformat())

    user = relationship("User", back_populates="likes")
    snippet = relationship("Snippet", back_populates="likes")


class AuthToken(Base):
    __tablename__ = 'auth_tokens'

    id = Column(Integer, primary_key=True)
    token = Column(String(64), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(String(256), default=lambda: datetime.utcnow().isoformat())

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)
