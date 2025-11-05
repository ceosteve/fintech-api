from fastapi import FastAPI

from app.routers import users

app = FastAPI()


app.include_router(users.router)


@app.get("/")
def get_root():
    return f"welcome to digital wallet"
