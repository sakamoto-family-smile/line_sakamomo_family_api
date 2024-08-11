import os
from logging import StreamHandler, getLogger

from fastapi import FastAPI, Header, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage
from pydantic import BaseModel
from starlette.exceptions import HTTPException

from .controller import Controller

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("DEBUG")


app = FastAPI(title="line_sakamomo_family_api", description="The API is sakamomo family bot.")
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
session_id = "sakamomo_family_session"
controller = Controller(dialogue_session_id=session_id)


class Response(BaseModel):
    status: str


@app.get("/health")
def health():
    return Response(status="OK")


@app.post(
    "/line_callback",
    summary="LINE Message APIからのコールバックです.",
    description="ユーザーからメッセージが送信された時に。本APIが呼び出されます.",
)
async def callback(request: Request, x_line_signature=Header(None)):

    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="InvalidSignatureError")
    return Response(status="OK")


@handler.add(MessageEvent)
def handle_message(event: MessageEvent):
    """
    LINE Messaging APIのハンドラより呼び出されます.

    Parameters
    ----------
    event : MessageEvent
        送信されたメッセージの情報です。
    """
    logger.info("start handle message...")
    logger.info(f"message event is {event.message}.")
    text = event.message.text

    # メッセージに対する処理を実施
    res = controller.handle_message(message=text)
    res_text = TextSendMessage(text=res)
    line_bot_api.reply_message(event.reply_token, res_text)
