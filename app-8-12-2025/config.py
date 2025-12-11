import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATABASE_URL = f"sqlite:///{BASE_DIR}/database.db"
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30