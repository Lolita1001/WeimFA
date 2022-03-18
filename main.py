from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from custom_logging import CustomizeLogger
from pathlib import Path
# import logging

from api.v1.user.route import api_router as user_route
from api.v1.media_user.route import api_router as media_user_route
from api.v1.security.route import api_router as security_route
from db.database import create_db_and_tables


# logger = logging.getLogger(__name__)


app = FastAPI()

config_path = Path(__file__).with_name("logging_config.json")
logger = CustomizeLogger.make_logger(config_path)
app.logger = logger

app.include_router(user_route, prefix='/api/v1/users')
app.include_router(media_user_route, prefix='/api/v1/media_user')
app.include_router(security_route, prefix='/api/v1/security')


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def redirect():
    return RedirectResponse("/docs")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)  # noqa
