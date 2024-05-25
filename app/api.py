import os
from logging import StreamHandler, getLogger

from fastapi import FastAPI, Header
from pydantic import BaseModel
from starlette.exceptions import HTTPException

from .controller import Controller


class Response(BaseModel):
    status: int
    message: str


class Request(BaseModel):
    message: str


logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("DEBUG")


app = FastAPI(title="sakamomo_family_api", description="The API is sakamomo family bot.")
session_id = "sakamomo_family_session"
controller = Controller(dialogue_session_id=session_id)


@app.get("/health")
def health():
    return Response(status=0, message="OK")


@app.post("/bot")
def bot(request: Request):
    try:
        res = controller.handle_message(message=request.message)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error. Bot process is failed.")
    return Response(status=0, message=res)
