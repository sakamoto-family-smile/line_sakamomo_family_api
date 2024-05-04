import os
from logging import StreamHandler, getLogger

from fastapi import FastAPI, Header, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage
from pydantic import BaseModel
from starlette.exceptions import HTTPException

from .agent import CustomAgent, CustomAgentConfig
from .todo_util import TodoHandler

logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("DEBUG")


app = FastAPI(title="line_sakamomo_family_api", description="The API is sakamomo family bot.")
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
session_id = "sakamomo_family_session"
agent_config = CustomAgentConfig(dialogue_session_id=session_id, memory_store_type="firestore")
local_agent = CustomAgent(agent_config=agent_config, logger=logger)
todo_handler = TodoHandler(collection_id="ToDoHistory", document_id=session_id, custom_logger=logger)


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

    # TODOの登録、取得処理を行う
    if text.startswith("TODO"):
        try:
            res = todo_handler.handle(input_text=text)
        except Exception as e:
            logger.error(e)
            res = "TODOの設定処理でエラーが発生しました."
    # LLMでの解析処理を実施
    else:
        try:
            res = local_agent.get_llm_agent_response(text=text).text
        except Exception as e:
            logger.error(e)
            res = "LLMのレスポンスでエラーが発生しました."
    res_text = TextSendMessage(text=res)
    line_bot_api.reply_message(event.reply_token, res_text)
