from fastapi import FastAPI
import uvicorn
import os
from fastapi.staticfiles import StaticFiles

from app.handlers import router as handlers_router
from app.auth import router as auth_router
from app.config import STATIC_DIR
from app.database import create_tables


def get_app() -> FastAPI:
    application = FastAPI(title="Code Snippets App")
    create_tables()
    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    application.include_router(handlers_router)
    application.include_router(auth_router)
    return application


app = get_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run("app.main:app", host='0.0.0.0', port=port)
