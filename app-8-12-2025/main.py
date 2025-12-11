from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from models import create_tables
from handlers import router

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
def on_startup():
    create_tables()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)