from fastapi import FastAPI

from app.logging.logging_middleware import LoggingMiddleWare
from app.routers import auth, transactions, users, wallets
from app.logging.logging_config import logging_setup

logging_setup()

app = FastAPI()

app.add_middleware(LoggingMiddleWare)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(wallets.router)
app.include_router(transactions.router)


@app.get("/")
def get_root():
    return f"welcome to digital wallet"
