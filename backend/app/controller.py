from logging import StreamHandler, getLogger
from .agent import CustomAgent, CustomAgentConfig
from .todo_util import TodoHandler


logger = getLogger(__name__)
logger.addHandler(StreamHandler())
logger.setLevel("DEBUG")


class Controller:
    def __init__(self, dialogue_session_id: str) -> None:
        agent_config = CustomAgentConfig(
            dialogue_session_id=dialogue_session_id,
            memory_store_type="firestore"
        )
        self.__agent = CustomAgent(agent_config=agent_config)
        self.__todo_handler = TodoHandler(
            family_id=agent_config.dialogue_session_id,
            collection_id="ToDoHistory",
            custom_logger=logger
        )

    # TODO : 内部で例外が発生した際は例外を返すようにした方がよさそう.
    def handle_message(self, message: str) -> str:
        # TODOの登録、取得処理を行う
        if message.startswith("TODO"):
            try:
                res = self.__todo_handler.handle(input_text=message)
            except Exception as e:
                logger.error(e)
                res = "TODOの設定処理でエラーが発生しました."
        # LLMでの解析処理を実施
        else:
            try:
                res = self.__agent.get_llm_agent_response(text=message).text
            except Exception as e:
                logger.error(e)
                res = "LLMのレスポンスでエラーが発生しました."
        return res
