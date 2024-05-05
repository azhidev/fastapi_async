from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request, Response, Header
from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import uvicorn, secrets, time, jwt, hashlib, dotenv, os, asyncio
from src import tasks
from src.apis import (
    users,
    # permissions
)
from src import models
from src.database import get_db
from utils.auth import get_user

dotenv.load_dotenv(os.path.join(".env"))


app = FastAPI(
    dependencies=[
        Depends(get_user),
        Depends(get_db),
    ],
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


router = APIRouter()
security = HTTPBasic()
router.include_router(users.router)
# router.include_router(permissions.router)
app.include_router(router)


@app.get("/")
async def root():
    return "APP RUNNING!"


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, os.environ.get("SWAGGER_USERNAME"))
    correct_password = secrets.compare_digest(credentials.password, os.environ.get("SWAGGER_PASSWORD"))
    if correct_username and correct_password:
        return credentials.username
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Basic"})


@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation(username: str = Depends(get_current_username)):
    return get_redoc_html(openapi_url="/openapi.json", title="docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title=app.title, version=app.version, routes=app.routes)


# @app.on_event("startup")
# async def task_manager():
#     loop = asyncio.get_event_loop()
#     loop.create_task(task_1.task())


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT")),
        reload=True,
        workers=int(os.environ.get("WORKER")),
        log_level="debug",
    )

"""
# add .env file
WORKER=
PORT=
RUNNING_MODE=
DEBUG_PASSWORD=
SECRET_KEY=
MY_SQL_ADDRESS=
ALGORITHM
"""
