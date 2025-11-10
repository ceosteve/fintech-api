from fastapi import FastAPI

from app.routers import auth, transactions, users, wallets

app = FastAPI()


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(wallets.router)
app.include_router(transactions.router)


@app.get("/")
def get_root():
    return f"welcome to digital wallet"
