from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api_cars import router as cars_router
from api_dealers import router as dealers_router
from api_dependencies import get_publisher

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    publisher = get_publisher()
    if publisher.init_infrastructure():
        print("RabbitMQ: инфраструктура готова")
    else:
        print("⚠️ RabbitMQ недоступен — API работает без событий")
    yield


app = FastAPI(
    title="Car Dealership Web API",
    description="ЛР3–6: REST, CRUD, события RabbitMQ, Web UI",
    version="4.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)
app.include_router(cars_router)
app.include_router(dealers_router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")

# pip install -r requirements.txt
# docker pull rabbitmq:3-management
# docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
# uvicorn api_main:app --reload
