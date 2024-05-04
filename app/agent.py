import os
from datetime import datetime
from logging import Logger, StreamHandler, getLogger
from typing import List, Optional, Type

import google.cloud.firestore
import requests
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.memory import ConversationBufferMemory
from langchain.tools.base import BaseTool
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_firestore import FirestoreChatMessageHistory
from langchain_google_vertexai import VertexAI
from pydantic import BaseModel

from .firebase_util import get_db_client_with_default_credentials

local_logger = getLogger(__name__)
local_logger.addHandler(StreamHandler())
local_logger.setLevel("DEBUG")


class WeatherInfo(BaseModel):
    area_name: str
    temperature: float
    pressure: int
    humidity: int
    weather: str


class LLMAgentResponse(BaseModel):
    text: str


class CustomAgentConfig(BaseModel):
    dialogue_session_id: str
    memory_store_type: str = "firestore"


class AgentUtil:
    @classmethod
    def get_weather_info(cls, area_name: str) -> WeatherInfo:
        api_key = os.environ["OPEN_WEATHER_KEY"]
        base_url = "http://api.openweathermap.org/data/2.5/weather"

        # TODO : area_nameを使うように修正(Tokyo,JPのように指定する)
        params = {"q": "Kanagawa-ken,JP", "units": "metric", "appid": api_key}

        # OpenWeatherMapにリクエストを投げて、天候情報を取得
        response = requests.get(base_url, params=params)
        data = response.json()
        if response.status_code == 200:
            info = WeatherInfo(
                area_name=data["name"],
                temperature=data["main"]["temp"],
                pressure=data["main"]["pressure"],
                humidity=data["main"]["humidity"],
                weather=data["weather"][0]["main"],
            )
        else:
            raise Exception(f"getting weather information is failed. http status code is {response.status_code}.")
        return info


class CustomAgent:
    def __init__(self, agent_config: CustomAgentConfig, logger: Logger = None) -> None:
        self.__agent_config = agent_config
        self.__logger = logger if logger is not None else local_logger

        # LLM Agentの作成
        llm = VertexAI(
            model_name="gemini-1.5-pro-preview-0409",
            temperature=0.5,
            max_output_tokens=400,
            location=os.environ["GCP_LOCATION"],
            project=os.environ["GCP_PROJECT"],
        )
        os.environ["OPENWEATHERMAP_API_KEY"] = os.environ["OPEN_WEATHER_KEY"]
        tools = self.get_tools(llm=llm)
        self.__agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
        )
        memory = self.get_chat_message_history(
            memory_type=self.__agent_config.memory_store_type,
            config={
                "session_id": self.__agent_config.dialogue_session_id,
                "collection": "HistoryMessages",
            },
        )
        self.__agent_with_chat_history = RunnableWithMessageHistory(
            self.__agent,
            # This is needed because in most real world scenarios, a session id is needed
            # It isn't really used here because we are using a simple in memory ChatMessageHistory
            lambda session_id: memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def get_weather_info(self, area_name: str) -> WeatherInfo:
        info = AgentUtil.get_weather_info(area_name=area_name)
        return info

    def get_llm_agent_response(self, text: str) -> LLMAgentResponse:
        self.__logger.info("start get_llm_agent_response...")
        res = self.__agent_with_chat_history.invoke(
            {"input": text},
            config={"configurable": {"session_id": self.__agent_config.dialogue_session_id}},
        )
        return LLMAgentResponse(text=res["output"])

    def get_chat_message_history(self, memory_type: str, config: dict) -> BaseChatMessageHistory:
        if memory_type == "local":
            chat_buffer = ConversationBufferMemory()
            return chat_buffer.chat_memory
        elif memory_type == "firestore":
            return FirestoreChatMessageHistory(session_id=config["session_id"], collection=config["collection"])
        else:
            raise NotImplementedError(f"{memory_type} memory type is not implemented!")

    def get_tools(self, llm) -> List[BaseTool]:
        tools = load_tools(["openweathermap-api"], llm)
        # tools.append(TodoRegisterTool(
        #    document_id=self.__agent_config.dialogue_session_id,
        #    logger=self.__logger
        # ))
        return tools


class TodoRegisterInput(BaseModel):
    target_date: datetime
    content: str


# TODO : 動かないので修正が必要
class TodoRegisterTool(BaseTool):
    name = "todo_register"
    description = "useful for when you need to register the task or todo."
    args_schema: Type[BaseModel] = TodoRegisterInput
    db: google.cloud.firestore.Client = None
    collection_id: str = "ToDoHistory"
    document_id: str = None
    logger = local_logger

    def __init__(self, /, **data) -> None:
        super().__init__(**data)
        self.db = get_db_client_with_default_credentials()
        self.collection_id = "ToDoHistory"
        self.document_id = data["document_id"]
        self.logger = data["logger"] if "logger" in data else local_logger

    def _run(
        self,
        target_date: datetime,
        content: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        self.logger.info(f"start to register the todo. date is {target_date}, todo content is {content}")
        try:
            data = {"date": target_date, "todo": content}
            self.db.collection(self.collection_id).document(self.document_id).set(data)
        except Exception as e:
            self.logger.error(e)
            return "error is occured!"
        return "LangChain"

    async def _arun(
        self,
        target_date: datetime,
        content: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
