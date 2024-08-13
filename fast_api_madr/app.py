from fastapi import FastAPI

from fast_api_madr.routers import account, auth

app = FastAPI()

app.include_router(auth.router)
app.include_router(account.router)


@app.get("/")
def read_root():
    return {"menssage": "Olá Mundo!"}
