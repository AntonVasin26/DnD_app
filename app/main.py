from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()


@app.get("/")
def read_root():
    return FileResponse("app/static/index.html")


@app.get("/api/status")
def status():
    return {"message": "Сервер работает!"}


# Важно: этот mount должен быть ПОСЛЕ всех @app.get(...) выше.
# FastAPI сначала проверяет отдельные маршруты ("/", "/api/status"),
# и только если ни один из них не подошёл — отдаёт запрос сюда,
# пытаясь найти файл внутри app/static по такому же относительному пути.
app.mount("/", StaticFiles(directory="app/static"), name="static")
