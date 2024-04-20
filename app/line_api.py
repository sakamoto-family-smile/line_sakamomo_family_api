import os
from fastapi import FastAPI, Header, Request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextSendMessage
from linebot.exceptions import InvalidSignatureError
from starlette.exceptions import HTTPException
from pydantic import BaseModel
from logging import getLogger, StreamHandler


logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("DEBUG")


app = FastAPI(
    title="line_sakamomo_family_api",
    description="The API is sakamomo family bot."
)
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])


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

    # debug
    logger.debug("start handle message...")
    logger.debug(event.message)

    res_text = TextSendMessage(text=f"レスポンスは実装中です. 送信されたメッセージは、{event.message.text}.")
    line_bot_api.reply_message(
        event.reply_token,
        res_text
    )
