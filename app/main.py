from fastapi import FastAPI
from app.handlers import router


def get_application():
    application = FastAPI()
    application.include_router(router)
    return application


app = get_application()
