from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from config.config import Settings

app = FastAPI(title="Hackaton Trivia API")
settings = Settings()
# CORS — должен быть до подключения роутеров
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# Подключаем роутеры ПОСЛЕ middleware
from controller.auth_controller import router as auth_router
from controller.room_controller import router as room_router

# Подключаем роуты
app.include_router(auth_router)
app.include_router(room_router)

# Главная страница (рендерит templates/index.html)
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Глобальный обработчик ошибок (опционально, но полезно)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "details": str(exc)}
    )


# Запуск через `python main.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host = settings.SERVER_HOST, port = 3425, reload = True)
