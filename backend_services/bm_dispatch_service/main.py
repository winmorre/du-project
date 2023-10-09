from fastapi import FastAPI

from src.helpers.log_configure import configure_logger

app = FastAPI(title='pipa', version="0.1.0")


@app.on_event("startup")
async def start():
    configure_logger(app=app)
